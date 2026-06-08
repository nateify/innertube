import json
import os
import re
import tempfile

from curl_cffi import requests


class StsResolver:
    def __init__(self, cache_file: str | None = None):
        if cache_file is None:
            self.cache_file = os.path.join(tempfile.gettempdir(), "innertube_sts_cache.json")
        else:
            self.cache_file = cache_file

        self.cache = self._load_cache()
        self._in_memory_sts = None
        self._in_memory_hash = None

    def _load_cache(self) -> dict:
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _save_cache(self):
        try:
            with open(self.cache_file, "w") as f:
                json.dump(self.cache, f)
        except Exception:
            pass

    def get_sts(self, impersonate: str = "chrome") -> int:
        if self._in_memory_sts is not None:
            return self._in_memory_sts

        resp = requests.get("https://www.youtube.com/iframe_api", impersonate=impersonate)
        resp.raise_for_status()

        hash_match = re.search(r"/s\\/player\\/([^/]+)\\/", resp.text)
        if not hash_match:
            raise RuntimeError("Could not extract player hash from iframe_api")

        player_hash = hash_match.group(1)
        self._in_memory_hash = player_hash

        if player_hash in self.cache:
            self._in_memory_sts = self.cache[player_hash]
            return self._in_memory_sts

        player_url = f"https://www.youtube.com/s/player/{player_hash}/player_ias.vflset/en_US/base.js"
        js_resp = requests.get(player_url, impersonate=impersonate)
        js_resp.raise_for_status()

        sts_match = re.search(r"signatureTimestamp\s*[=:]\s*(\d+)|sts\s*[=:]\s*(\d+)", js_resp.text)
        if not sts_match:
            raise RuntimeError("Could not find signatureTimestamp in base.js")

        sts = int(sts_match.group(1) or sts_match.group(2))

        self.cache[player_hash] = sts
        self._save_cache()

        self._in_memory_sts = sts
        return sts
