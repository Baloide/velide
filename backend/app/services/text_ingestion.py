"""Read one local document in memory; never save an upload or change the source."""

import logging
from io import BytesIO
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile

from docx import Document
from docx.table import Table
from pypdf import PdfReader, apply_configuration
from pypdf.errors import LimitReachedError

from app.schemas.ingest import FileFormat, IngestResponse

MAX_FILE_BYTES = 10 * 1024 * 1024
MAX_TEXT_CHARACTERS = 200_000
MAX_PDF_PAGES = 200
MAX_DOCX_EXPANDED_BYTES = 30 * 1024 * 1024
MAX_PDF_STREAM_BYTES = 5 * 1024 * 1024

# Parser diagnostics can contain document content. Return stable codes instead.
logging.getLogger("pypdf").addHandler(logging.NullHandler())
logging.getLogger("pypdf").propagate = False


class IngestionError(Exception):
    """Stable, non-sensitive error code and HTTP status for an import failure."""

    def __init__(self, code: str, status: int = 422):
        self.code = code
        self.status = status
        super().__init__(code)


class TextCollector:
    """Accumulate extracted fragments while enforcing the total text budget."""

    def __init__(self):
        self.parts = []
        self.size = 0

    def add(self, value):
        if not value.strip():
            return
        self.size += len(value) + (1 if self.parts else 0)
        if self.size > MAX_TEXT_CHARACTERS:
            raise IngestionError("textTooLong", 413)
        self.parts.append(value)

    def text(self):
        return "\n".join(self.parts).strip()


def _blocks(container, collector, depth=0):
    """Traverse Word blocks in document order, retaining tab-separated table cells.

    Args:
        container: A document, header, footer, or table cell.
        collector: Recipient of the extracted paragraphs and rows.
        depth: Current nesting level for the table recursion guard.

    Raises:
        IngestionError: The nesting or extracted-text budget was exceeded.
    """
    if depth > 20:
        raise IngestionError("documentTooComplex", 413)
    for block in container.iter_inner_content():
        if isinstance(block, Table):
            for row in block.rows:
                seen = set()
                cells = []
                for cell in row.cells:
                    # Merged cells can be returned more than once.
                    if cell._tc not in seen:
                        seen.add(cell._tc)
                        cell_text = TextCollector()
                        _blocks(cell, cell_text, depth + 1)
                        cells.append(cell_text.text())
                # Keep field labels next to their values so rules still see
                # e.g. "Paziente:\tMario Rossi" across neighboring cells.
                collector.add("\t".join(cells))
        else:
            collector.add(block.text)


def _docx(data, collector):
    try:
        with ZipFile(BytesIO(data)) as archive:
            entries = archive.infolist()
            if (
                len(entries) > 1000
                or sum(entry.file_size for entry in entries) > MAX_DOCX_EXPANDED_BYTES
            ):
                raise IngestionError("documentTooComplex", 413)
            if "word/document.xml" not in archive.namelist():
                raise IngestionError("unreadableFile")
            if any(entry.compress_type not in (ZIP_STORED, ZIP_DEFLATED) for entry in entries):
                raise IngestionError("unreadableFile")
        document = Document(BytesIO(data))
        seen = set()
        for section in document.sections:
            for header in (section.header, section.first_page_header, section.even_page_header):
                key = str(header.part.partname)
                if key not in seen:
                    seen.add(key)
                    _blocks(header, collector)
        _blocks(document, collector)
        for section in document.sections:
            for footer in (section.footer, section.first_page_footer, section.even_page_footer):
                key = str(footer.part.partname)
                if key not in seen:
                    seen.add(key)
                    _blocks(footer, collector)
    except IngestionError:
        raise
    except Exception:
        # Do not include parser exception strings, which can contain private data.
        raise IngestionError("unreadableFile") from None


def _pdf(data, collector):
    if not data.lstrip().startswith(b"%PDF-"):
        raise IngestionError("unreadableFile")
    try:
        with apply_configuration(
            maximum_declared_stream_length=MAX_FILE_BYTES,
            array_based_stream_maximum_output_length=MAX_PDF_STREAM_BYTES,
            zlib_maximum_output_length=MAX_PDF_STREAM_BYTES,
            lzw_maximum_output_length=MAX_PDF_STREAM_BYTES,
            run_length_maximum_output_length=MAX_PDF_STREAM_BYTES,
            brotli_maximum_output_length=MAX_PDF_STREAM_BYTES,
            jbig2_maximum_output_length=MAX_PDF_STREAM_BYTES,
            image_maximum_buffer_size=MAX_PDF_STREAM_BYTES,
            stream_decoding_work_maximum_length=4 * MAX_PDF_STREAM_BYTES,
            page_tree_maximum_entries=2000,
            xform_maximum_invocations_per_extraction=128,
            jbig2dec_binary=None,
        ):
            return _pdf_pages(data, collector)
    except IngestionError:
        raise
    except LimitReachedError:
        raise IngestionError("documentTooComplex", 413) from None
    except Exception:
        raise IngestionError("unreadableFile") from None


def _pdf_pages(data, collector):
    """Read PDF pages within the request-scoped decoder configuration."""
    reader = PdfReader(BytesIO(data))
    if reader.is_encrypted:
        raise IngestionError("encryptedPdf")
    count = len(reader.pages)
    if count > MAX_PDF_PAGES:
        raise IngestionError("tooManyPages", 413)
    empty_pages = []
    for number, page in enumerate(reader.pages, 1):
        content = page.get_contents()
        if content is not None and len(content.get_data()) > MAX_PDF_STREAM_BYTES:
            raise IngestionError("documentTooComplex", 413)
        value = page.extract_text() or ""
        if not value.strip():
            empty_pages.append(number)
        collector.add(value)
    if not collector.text():
        raise IngestionError("pdfNoText")
    return count, empty_pages


def _plain(data):
    try:
        if data.startswith((b"\xff\xfe", b"\xfe\xff")):
            value = data.decode("utf-16")
        else:
            try:
                value = data.decode("utf-8-sig")
            except UnicodeDecodeError:
                value = data.decode("cp1252")
    except UnicodeError:
        raise IngestionError("textEncoding") from None
    if any(ord(character) < 32 and character not in "\r\n\t\f" for character in value):
        raise IngestionError("textEncoding")
    return value.replace("\r\n", "\n").replace("\r", "\n")


def extract_text(data: bytes, format: FileFormat) -> IngestResponse:
    """Extract one uploaded document entirely within application memory.

    Args:
        data: Raw bytes; the application does not write them to a temporary file.
        format: Validated format key (pdf, docx, txt, or md).

    Returns:
        Plain text, lengths, PDF page counts, and stable warning codes.

    Raises:
        IngestionError: Unsupported, corrupt, empty, encrypted, or oversized input.

    This does not preserve visual layout or perform OCR. In-memory processing
    is not a guarantee about operating-system swap, dumps, or browser storage.
    """
    if len(data) > MAX_FILE_BYTES:
        raise IngestionError("fileTooLarge", 413)
    if not data:
        raise IngestionError("emptyFile")
    collector = TextCollector()
    pages, empty_pages, warnings = None, [], []
    if format == "pdf":
        pages, empty_pages = _pdf(data, collector)
        warnings.append("importReview")
        if empty_pages:
            warnings.append("partialPdf")
    elif format == "docx":
        _docx(data, collector)
        warnings.extend(["importReview", "docxReview"])
    elif format in ("txt", "md"):
        collector.add(_plain(data))
    else:
        raise IngestionError("unsupportedFile", 415)
    text = collector.text()
    if not text:
        raise IngestionError("emptyFile")
    return IngestResponse(
        text=text,
        format=format,
        characters=len(text),
        pages=pages,
        pages_without_text=empty_pages,
        warnings=warnings,
    )
