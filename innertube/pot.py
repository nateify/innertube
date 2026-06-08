from typing import Optional

from curl_cffi.requests import Session


class PoTokenProvider:
    def __init__(self, base_url: str = "http://127.0.0.1:4416", session: Optional[Session] = None):
        if not base_url.startswith("http://"):
            base_url = f"http://{base_url}"

        self.base_url = base_url.rstrip("/")
        self.session = session or Session

    def get_po_token(self, content_binding: str, innertube_context: dict) -> str:
        payload = {"content_binding": content_binding, "innertube_context": innertube_context}
        response = self.session.post(f"{self.base_url}/get_pot", json=payload, timeout=20.0)
        response.raise_for_status()

        data = response.json()
        if "error" in data:
            raise RuntimeError(f"PoTokenProvider Error: {data['error']}")

        po_token = data.get("poToken")
        if not po_token:
            raise RuntimeError("PoTokenProvider Error: Server did not respond with a poToken")

        return po_token
