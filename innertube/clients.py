import dataclasses
import re
from typing import List, Optional, Union

import mediate
from curl_cffi import requests

from . import api, utils
from .adaptor import InnerTubeAdaptor
from .enums import Endpoint
from .locale import Locale
from .models import ClientContext
from .pot import PoTokenProvider
from .protocols import Adaptor
from .sts import StsResolver

_sts_resolver = StsResolver()


@dataclasses.dataclass
class Client:
    adaptor: Adaptor

    middleware: mediate.Middleware = dataclasses.field(default_factory=mediate.Middleware, repr=False, init=False)

    def __call__(
        self, endpoint: str, params: Optional[dict] = None, body: Optional[dict] = None, po_token: Optional[str] = None
    ) -> dict:
        @self.middleware.bind
        def process(data: dict, /) -> dict:
            return data

        response: dict = process(self.adaptor.dispatch(endpoint, params=params, body=body, po_token=po_token))

        response.pop("responseContext")

        return response


@dataclasses.dataclass(init=False)
class InnerTube(Client):
    def __init__(
        self,
        client_name: str,
        client_version: Optional[str] = None,
        *,
        api_key: Optional[str] = None,
        user_agent: Optional[str] = None,
        referer: Optional[str] = None,
        locale: Optional[Locale] = None,
        auto: bool = True,
        proxy: Optional[Union[str, dict]] = None,
        pot_provider_url: str = "http://127.0.0.1:4416",
    ) -> None:
        if client_name is None:
            raise ValueError("Precondition failed: Missing client name")

        kwargs: dict = utils.filter(
            dict(
                client_name=client_name,
                client_version=client_version,
                api_key=api_key,
                user_agent=user_agent,
                referer=referer,
                locale=locale,
            )
        )

        context: ClientContext

        auto_context: Optional[ClientContext]
        if auto and (auto_context := api.get_context(client_name)):
            context = dataclasses.replace(auto_context, **kwargs)
        else:
            if client_version is None:
                raise ValueError("Precondition failed: Missing client version")

            context = ClientContext(**kwargs)

        if proxy is not None:
            if isinstance(proxy, str):
                proxies = {"http": proxy, "https": proxy}
            else:
                proxies = proxy
        else:
            proxies = None

        session = requests.Session(
            impersonate=context.impersonate,
            proxies=proxies,
        )

        pot_provider = PoTokenProvider(base_url=pot_provider_url) if pot_provider_url else None

        super().__init__(
            adaptor=InnerTubeAdaptor(
                context=context,
                session=session,
                pot_provider=pot_provider,
            )
        )

    def config(self) -> dict:
        return self(Endpoint.CONFIG)

    def guide(self) -> dict:
        return self(Endpoint.GUIDE)

    def player(
        self,
        video_id: str,
        *,
        params: Optional[str] = None,
        signature_timestamp: Optional[int] = None,
    ) -> dict:
        # Bootstrap session cookies - experimental, not required
        # if "WEB" in self.adaptor.context.client_name.upper() and not self.adaptor.session.cookies:
        #     bootstrap_url = f"https://www.youtube.com/watch?v={video_id}&bpctr=9999999999&has_verified=1"
        #     try:
        #         resp = self.adaptor.session.get(bootstrap_url, headers=self.adaptor.context.headers(), timeout=10.0)
        #
        #         visitor_match = re.search(r'["\']VISITOR_DATA["\']\s*:\s*["\']([^"\']+)["\']', resp.text)
        #         if visitor_match:
        #             visitor_data = visitor_match.group(1)
        #             visitor_data = visitor_data.encode().decode("unicode_escape")
        #             self.adaptor.session.headers["X-Goog-Visitor-Id"] = visitor_data
        #     except Exception:
        #         pass

        is_embedded = self.adaptor.context.payload_name == "WEB_EMBEDDED_PLAYER"
        encrypted_host_flags = None
        embedded_player_context = None

        if is_embedded:
            embed_url = f"https://www.youtube.com/embed/{video_id}?html5=1"
            try:
                headers = self.adaptor.context.headers()
                resp = self.adaptor.session.get(embed_url, headers=headers, timeout=10.0)

                ehf_match = re.search(r'["\']encryptedHostFlags["\']\s*:\s*["\']([^"\']+)["\']', resp.text)
                if ehf_match:
                    encrypted_host_flags = ehf_match.group(1).encode().decode("unicode_escape")

                epc_match = re.search(r'["\']embeddedPlayerEncryptedContext["\']\s*:\s*["\']([^"\']+)["\']', resp.text)
                if epc_match:
                    embedded_player_context = epc_match.group(1).encode().decode("unicode_escape")
            except Exception:
                pass

        body = {
            "videoId": video_id,
            "contentCheckOk": True,
            "racyCheckOk": True,
        }

        if params is not None:
            body["params"] = params

        needs_sts = self.adaptor.context.payload_name in ("WEB", "WEB_REMIX", "TVHTML5", "WEB_EMBEDDED_PLAYER")

        if signature_timestamp is None and needs_sts:
            signature_timestamp = _sts_resolver.get_sts(impersonate=self.adaptor.context.impersonate)

        playback_context = {"contentPlaybackContext": {"html5Preference": "HTML5_PREF_WANTS"}}
        if signature_timestamp is not None:
            playback_context["contentPlaybackContext"]["signatureTimestamp"] = signature_timestamp

        if is_embedded:
            if encrypted_host_flags:
                playback_context["contentPlaybackContext"]["encryptedHostFlags"] = encrypted_host_flags

            if embedded_player_context:
                body.setdefault("context", {}).setdefault("thirdParty", {}).update(
                    {
                        "embeddedPlayerContext": {
                            "embeddedPlayerEncryptedContext": embedded_player_context,
                            "ancestorOriginsSupported": False,
                        }
                    }
                )

        body["playbackContext"] = playback_context

        response = self(Endpoint.PLAYER, body=body)

        playability_status = response.get("playabilityStatus", {})
        status = playability_status.get("status")

        is_age_gated = "confirm your age" in playability_status.get("reason", "").lower() or status in (
            "AGE_CHECK_REQUIRED",
            "AGE_VERIFICATION_REQUIRED",
        )

        if is_age_gated and self.adaptor.context.client_name != "WEB_EMBEDDED":
            embedded_context = api.get_context("WEB_EMBEDDED")
            if embedded_context:
                self.adaptor.set_context(embedded_context)
                return self.player(video_id, params=params, signature_timestamp=signature_timestamp)

        # is_bot_challenged = status == "LOGIN_REQUIRED" and "confirm" in playability_status.get("reason", "").lower()
        #
        # if is_bot_challenged and self.adaptor.pot_provider is not None:
        #     visitor_data = self.adaptor.session.headers.get("X-Goog-Visitor-Id")
        #
        #     mock_context = {"client": self.adaptor.context.context()}
        #     if visitor_data:
        #         mock_context["client"]["visitorData"] = visitor_data
        #
        #     try:
        #         po_token = self.adaptor.pot_provider.get_po_token(
        #             content_binding=video_id, innertube_context=mock_context
        #         )
        #         if po_token:
        #             return self(Endpoint.PLAYER, body=body, po_token=po_token)
        #     except Exception:
        #         pass

        return response

    def browse(
        self,
        browse_id: Optional[str] = None,
        *,
        params: Optional[str] = None,
        continuation: Optional[str] = None,
    ) -> dict:
        return self(
            Endpoint.BROWSE,
            body=utils.filter(
                dict(
                    browseId=browse_id,
                    params=params,
                    continuation=continuation,
                )
            ),
        )

    def search(
        self,
        query: Optional[str] = None,
        *,
        params: Optional[str] = None,
        continuation: Optional[str] = None,
    ) -> dict:
        return self(
            Endpoint.SEARCH,
            body=utils.filter(
                dict(
                    query=query or "",
                    params=params,
                    continuation=continuation,
                )
            ),
        )

    def next(
        self,
        video_id: Optional[str] = None,
        playlist_id: Optional[str] = None,
        *,
        params: Optional[str] = None,
        index: Optional[int] = None,
        continuation: Optional[str] = None,
    ) -> dict:
        return self(
            Endpoint.NEXT,
            body=utils.filter(
                dict(
                    params=params,
                    playlistId=playlist_id,
                    videoId=video_id,
                    playlistIndex=index,
                    continuation=continuation,
                )
            ),
        )

    def get_transcript(
        self,
        params: str,
    ) -> dict:
        return self(
            Endpoint.GET_TRANSCRIPT,
            body=utils.filter(
                dict(
                    params=params,
                )
            ),
        )

    def music_get_search_suggestions(
        self,
        input: Optional[str] = None,
    ) -> dict:
        return self(
            Endpoint.MUSIC_GET_SEARCH_SUGGESTIONS,
            body=dict(
                input=input or "",
            ),
        )

    def music_get_queue(
        self,
        *,
        video_ids: Optional[List[str]] = None,
        playlist_id: Optional[str] = None,
    ) -> dict:
        return self(
            Endpoint.MUSIC_GET_QUEUE,
            body=utils.filter(
                dict(
                    playlistId=playlist_id,
                    videoIds=video_ids or (None,),
                )
            ),
        )
