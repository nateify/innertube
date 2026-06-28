import dataclasses
import http
from typing import Dict, List, Optional

from . import utils
from .locale import Locale


@dataclasses.dataclass
class Error:
    code: int
    message: str
    reason: str

    def __str__(self) -> str:
        return f"{self.code} {self.status.phrase}: {self.message}"

    @property
    def status(self) -> http.HTTPStatus:
        return http.HTTPStatus(self.code)


@dataclasses.dataclass
class ClientContext:
    client_name: str
    client_version: str
    device_make: Optional[str] = None
    device_model: Optional[str] = None
    android_sdk_version: Optional[int] = None
    os_name: Optional[str] = None
    os_version: Optional[str] = None
    client_id: Optional[int] = None
    api_key: Optional[str] = None
    user_agent: Optional[str] = None
    impersonate_target: Optional[str] = None
    referer: Optional[str] = None
    locale: Optional[Locale] = None

    @property
    def payload_name(self) -> str:
        name_upper = self.client_name.upper()
        if "SAFARI" in name_upper:
            return "WEB"
        if "EMBEDDED" in name_upper:
            return "WEB_EMBEDDED_PLAYER"
        if name_upper == "TV":
            return "TVHTML5"
        if "MUSIC" in name_upper:
            return "WEB_REMIX"
        return self.client_name

    @property
    def impersonate(self) -> str | None:
        if self.impersonate_target or self.impersonate_target is None:
            return self.impersonate_target
        if "IOS" in self.client_name.upper():
            return "safari_ios"
        return "chrome"

    def params(self) -> Dict[str, str]:
        return utils.filter(
            {
                "key": self.api_key,
                "alt": "json",
            }
        )

    def context(self) -> dict[str, int | str]:
        return utils.filter(
            {
                "clientName": self.payload_name,
                "clientVersion": self.client_version,
                "deviceMake": self.device_make if self.device_make is not None else None,
                "deviceModel": self.device_model if self.device_model is not None else None,
                "androidSdkVersion": self.android_sdk_version if self.android_sdk_version is not None else None,
                "osName": self.os_name if self.os_name is not None else None,
                "osVersion": self.os_version if self.os_version is not None else None,
                "gl": self.locale.location if self.locale is not None else "US",
                "hl": self.locale.language if self.locale is not None else "en",
                "userAgent": self.user_agent,
                "timeZone":         "UTC",
                "utcOffsetMinutes": 0,
            }
        )

    def headers(self) -> Dict[str, str]:
        origin = "https://www.youtube.com"
        if self.referer and "music.youtube.com" in self.referer:
            origin = "https://music.youtube.com"
        elif self.referer and "youtube.com" in self.referer:
            origin = "https://www.youtube.com"

        return utils.filter(
            {
                "X-Goog-Api-Format-Version": "1",
                "X-YouTube-Client-Name": str(self.client_id),
                "X-YouTube-Client-Version": self.client_version,
                "Origin": origin,
                "User-Agent": self.user_agent,
                "Referer": self.referer,
                "Accept-Language": (self.locale.accept_language() if self.locale is not None else None),
            }
        )


@dataclasses.dataclass
class Config:
    base_url: str
    clients: List[ClientContext]


@dataclasses.dataclass
class ResponseContext:
    @dataclasses.dataclass
    class Request:
        type: Optional[str] = None
        id: Optional[str] = None

    @dataclasses.dataclass
    class Client:
        name: Optional[str] = None
        version: Optional[str] = None

    @dataclasses.dataclass
    class Flags:
        logged_in: Optional[bool] = None

    function: Optional[str] = None
    browse_id: Optional[str] = None
    context: Optional[str] = None
    visitor_data: Optional[str] = None
    client: Client = dataclasses.field(default_factory=Client)
    request: Request = dataclasses.field(default_factory=Request)
    flags: Flags = dataclasses.field(default_factory=Flags)


@dataclasses.dataclass
class ResponseFingerprint:
    request: Optional[str] = None
    function: Optional[str] = None
    browse_id: Optional[str] = None
    context: Optional[str] = None
    client: Optional[str] = None
