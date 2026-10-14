from typing import Literal

from pydantic import BaseModel, Field

FileFormat = Literal["pdf", "docx", "txt", "md"]


class IngestResponse(BaseModel):
    text: str
    format: FileFormat
    characters: int
    pages: int | None = None
    pages_without_text: list[int] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
