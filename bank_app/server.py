from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from .exceptions import BankError, ValidationError
from .service import BankService

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
SERVICE = BankService()


class BankRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        parsed_path = urlparse(self.path)
        if parsed_path.path == "/":
            self._serve_index()
            return
        if parsed_path.path == "/api/state":
            self._send_json(HTTPStatus.OK, SERVICE.get_snapshot())
            return
        if parsed_path.path.startswith("/static/"):
            self._serve_static(parsed_path.path.removeprefix("/static/"))
            return
        self._send_json(HTTPStatus.NOT_FOUND, {"error": "Route not found."})

    def do_POST(self) -> None:  # noqa: N802
        parsed_path = urlparse(self.path)
        try:
            payload = self._read_json()
            if parsed_path.path == "/api/accounts":
                account = SERVICE.create_account(payload.get("accountNumber"))
                self._send_json(
                    HTTPStatus.CREATED,
                    {
                        "message": f"Account {account.account_number} created successfully.",
                        "state": SERVICE.get_snapshot(),
                    },
                )
                return
            if parsed_path.path == "/api/deposit":
                account = SERVICE.deposit(
                    payload.get("accountNumber"), payload.get("amount")
                )
                self._send_json(
                    HTTPStatus.OK,
                    {
                        "message": f"Deposit completed for {account.account_number}.",
                        "state": SERVICE.get_snapshot(),
                    },
                )
                return
            if parsed_path.path == "/api/withdraw":
                account = SERVICE.withdraw(
                    payload.get("accountNumber"), payload.get("amount")
                )
                self._send_json(
                    HTTPStatus.OK,
                    {
                        "message": f"Withdrawal completed for {account.account_number}.",
                        "state": SERVICE.get_snapshot(),
                    },
                )
                return
            if parsed_path.path == "/api/transfer":
                result = SERVICE.transfer(
                    payload.get("senderAccountNumber"),
                    payload.get("recipientAccountNumber"),
                    payload.get("amount"),
                )
                self._send_json(
                    HTTPStatus.OK,
                    {
                        "message": (
                            f"Transferred ${float(payload.get('amount')):,.2f} from "
                            f"{result['sender'].account_number} to "
                            f"{result['recipient'].account_number}."
                        ),
                        "state": SERVICE.get_snapshot(),
                    },
                )
                return
            if parsed_path.path == "/api/lock":
                account = SERVICE.lock_account(payload.get("accountNumber"))
                self._send_json(
                    HTTPStatus.OK,
                    {
                        "message": f"Account {account.account_number} locked.",
                        "state": SERVICE.get_snapshot(),
                    },
                )
                return
            if parsed_path.path == "/api/unlock":
                account = SERVICE.unlock_account(payload.get("accountNumber"))
                self._send_json(
                    HTTPStatus.OK,
                    {
                        "message": f"Account {account.account_number} unlocked.",
                        "state": SERVICE.get_snapshot(),
                    },
                )
                return
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "Route not found."})
        except json.JSONDecodeError:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "Request body must be JSON."})
        except ValidationError as exc:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
        except ValueError as exc:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
        except BankError as exc:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        # Keep terminal output focused on meaningful app events.
        return

    def _read_json(self) -> dict:
        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length) if content_length else b"{}"
        return json.loads(raw_body.decode("utf-8"))

    def _serve_index(self) -> None:
        html = (TEMPLATES_DIR / "index.html").read_text(encoding="utf-8")
        self._send_response(HTTPStatus.OK, html.encode("utf-8"), "text/html; charset=utf-8")

    def _serve_static(self, relative_path: str) -> None:
        safe_path = (STATIC_DIR / relative_path).resolve()
        if not str(safe_path).startswith(str(STATIC_DIR.resolve())) or not safe_path.exists():
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "Static file not found."})
            return

        mime_type = "text/plain; charset=utf-8"
        if safe_path.suffix == ".css":
            mime_type = "text/css; charset=utf-8"
        elif safe_path.suffix == ".js":
            mime_type = "application/javascript; charset=utf-8"

        self._send_response(HTTPStatus.OK, safe_path.read_bytes(), mime_type)

    def _send_json(self, status: HTTPStatus, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self._send_response(status, body, "application/json; charset=utf-8")

    def _send_response(self, status: HTTPStatus, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def run(host: str = "127.0.0.1", port: int = 8000) -> None:
    with ThreadingHTTPServer((host, port), BankRequestHandler) as server:
        print(f"Bank dashboard running at http://{host}:{port}")
        server.serve_forever()
