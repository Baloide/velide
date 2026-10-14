"""Private loopback service owned by the Electron desktop process."""

import json
import socket
import sys
import threading
import time
from pathlib import Path

if not getattr(sys, "frozen", False):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

import uvicorn
from app.main import app


def main():
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        listener.bind(("127.0.0.1", 8760))
    except OSError:
        listener.bind(("127.0.0.1", 0))
    listener.listen(128)
    server = uvicorn.Server(
        uvicorn.Config(
            app,
            log_config=None,
            log_level="critical",
            access_log=False,
            loop="asyncio",
            http="h11",
            ws="none",
        )
    )
    worker = threading.Thread(target=server.run, kwargs={"sockets": [listener]}, daemon=True)
    worker.start()
    deadline = time.monotonic() + 30
    while not server.started:
        if not worker.is_alive() or time.monotonic() > deadline:
            raise SystemExit(1)
        time.sleep(0.05)
    print(json.dumps({"url": f"http://127.0.0.1:{listener.getsockname()[1]}"}), flush=True)
    # Electron owns this pipe. EOF shuts down the service even if its parent crashes.
    try:
        for _ in sys.stdin:
            pass
    finally:
        server.should_exit = True
        worker.join(timeout=5)
        listener.close()


if __name__ == "__main__":
    main()
