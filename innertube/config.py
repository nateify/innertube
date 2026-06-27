from .models import ClientContext, Config

REFERER_YOUTUBE: str = "https://www.youtube.com/"
REFERER_YOUTUBE_MUSIC: str = "https://music.youtube.com/"
REFERER_EMBED_THIRD_PARTY: str = "https://www.reddit.com/"

config: Config = Config(
    base_url="https://youtubei.googleapis.com/youtubei/v1/",
    clients=[
        ClientContext(
            client_id=28,
            client_name="ANDROID_VR",
            client_version="1.65.10",
            user_agent="com.google.android.apps.youtube.vr.oculus/1.65.10 (Linux; U; Android 12L; eureka-user Build/SQ3A.220605.009.A1) gzip",
        ),
        ClientContext(
            client_id=5,
            client_name="IOS",
            client_version="21.02.3",
            user_agent="com.google.ios.youtube/21.02.3 (iPhone16,2; U; CPU iOS 18_3_2 like Mac OS X;)",
            api_key="AIzaSyB-63vPrdThhKuerbB2N_l7Kwwcxj6yUAc",
        ),
        ClientContext(
            client_id=1,
            client_name="WEB",
            client_version="2.20260114.08.00",
            referer=REFERER_YOUTUBE,
            api_key="AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8",
        ),
        ClientContext(
            client_id=1,
            client_name="WEB_SAFARI",
            client_version="2.20260114.08.00",
            referer=REFERER_YOUTUBE,
            impersonate_target="safari",
            api_key="AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8",
        ),
        ClientContext(
            client_id=56,
            client_name="WEB_EMBEDDED",
            client_version="1.20260115.01.00",
            referer=REFERER_EMBED_THIRD_PARTY,
        ),
        ClientContext(
            client_id=67,
            client_name="WEB_MUSIC",
            client_version="1.20260114.03.00",
            referer=REFERER_YOUTUBE_MUSIC,
            api_key="AIzaSyC9XL3ZjWddXya6X74dJoCTL-WEYFDNX30",
        ),
        ClientContext(
            client_id=7,
            client_name="TV",
            client_version="7.20260114.12.00",
            user_agent="Mozilla/5.0 (ChromiumStylePlatform) Cobalt/25.lts.30.1034943-gold (unlike Gecko), Unknown_TV_Unknown_0/Unknown (Unknown, Unknown)",
        ),
    ],
)
