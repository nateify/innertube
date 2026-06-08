import urllib.parse
from typing import Optional

from curl_cffi import requests

from . import api
from .config import config
from .errors import RequestError, ResponseError
from .models import ClientContext
from .pot import PoTokenProvider


class InnerTubeAdaptor:
    context: ClientContext
    session: requests.Session
    pot_provider: Optional[PoTokenProvider]

    def __init__(
        self,
        context: ClientContext,
        session: Optional[requests.Session] = None,
        pot_provider: Optional[PoTokenProvider] = None,
    ) -> None:
        self.context = context
        self.session = session or requests.Session(impersonate=context.impersonate)
        self.pot_provider = pot_provider

    def __repr__(self) -> str:
        return f"{type(self).__name__}(context={self.context!r})"

    def _request(self, endpoint: str, params: Optional[dict] = None, body: Optional[dict] = None) -> requests.Response:
        req_params = self.context.params()
        if params:
            req_params.update(params)

        visitor_data = self.session.headers.get("X-Goog-Visitor-Id")
        payload = api.contextualise(self.context, body or {}, visitor_data=visitor_data)

        if self.pot_provider is not None:
            # videoId is used for content-bound tokens (Player), visitor_data used for session-bound
            content_binding = payload.get("videoId")
            if not content_binding:
                content_binding = visitor_data or ""

            innertube_context = payload.get("context", {})
            try:
                po_token = self.pot_provider.get_po_token(content_binding, innertube_context)
                if po_token:
                    payload.setdefault("serviceIntegrityDimensions", {})["poToken"] = po_token
            except Exception:
                pass

        url = urllib.parse.urljoin(config.base_url, endpoint)

        return self.session.request(
            "POST",
            url,
            params=req_params,
            json=payload,
            headers=self.context.headers(),
        )

    def dispatch(self, endpoint: str, params: Optional[dict] = None, body: Optional[dict] = None) -> dict:
        response: requests.Response = self._request(endpoint, params=params, body=body)

        content_type: Optional[str] = response.headers.get("Content-Type")

        if content_type is not None:
            if not content_type.lower().startswith("application/json"):
                raise ResponseError(f"Expected JSON response, got {content_type!r}")

        response_data: dict = response.json()

        visitor_data: Optional[str] = response_data.get("responseContext", {}).get("visitorData")

        if visitor_data is not None:
            self.session.headers["X-Goog-Visitor-Id"] = visitor_data

        error: Optional[dict] = response_data.get("error")

        if error is not None:
            raise RequestError(api.error(error))

        return response_data
