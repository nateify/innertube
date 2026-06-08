from .models import ClientContext, Config

REFERER_YOUTUBE: str = "https://www.youtube.com/"
REFERER_YOUTUBE_MOBILE: str = "https://m.youtube.com/"
REFERER_YOUTUBE_MUSIC: str = "https://music.youtube.com/"
REFERER_YOUTUBE_KIDS: str = "https://www.youtubekids.com/"
REFERER_YOUTUBE_STUDIO: str = "https://studio.youtube.com/"
REFERER_YOUTUBE_ANALYTICS: str = "https://analytics.youtube.com/"

USER_AGENT_IOS: str = "com.google.ios.youtube/21.02.3 (iPhone16,2; U; CPU iOS 18_3_2 like Mac OS X;)"

config: Config = Config(
    base_url="https://youtubei.googleapis.com/youtubei/v1/",
    clients=[
        ClientContext(
            client_id=1,
            client_name="WEB",
            client_version="2.20260206.01.00",
            referer=REFERER_YOUTUBE,
            api_key="AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8",
        ),
        ClientContext(
            client_id=2,
            client_name="MWEB",
            client_version="2.20260205.04.01",
            referer=REFERER_YOUTUBE_MOBILE,
            api_key="AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8",
        ),
        ClientContext(
            client_id=5,
            client_name="IOS",
            client_version="21.02.3",
            user_agent=USER_AGENT_IOS,
            api_key="AIzaSyB-63vPrdThhKuerbB2N_l7Kwwcxj6yUAc",
        ),
        ClientContext(
            client_id=15,
            client_name="IOS_CREATOR",
            client_version="20.47.100",
            user_agent=USER_AGENT_IOS,
            api_key="AIzaSyAPyF5GfQI-kOa6nZwO8EsNrGdEx9bioNs",
        ),
        ClientContext(
            client_id=19,
            client_name="IOS_KIDS",
            client_version="5.42.2",
            user_agent=USER_AGENT_IOS,
            api_key="AIzaSyA6_JWXwHaVBQnoutCv1-GvV97-rJ949Bc",
        ),
        ClientContext(
            client_id=26,
            client_name="IOS_MUSIC",
            client_version="4.16.1",
            user_agent=USER_AGENT_IOS,
            api_key="AIzaSyBAETezhkwP0ZWA02RsqT1zu78Fpt0bC_s",
        ),
        ClientContext(
            client_id=31,
            client_name="WEB_MUSIC_ANALYTICS",
            client_version="0.2",
            referer=REFERER_YOUTUBE_ANALYTICS,
        ),
        ClientContext(
            client_id=42,
            client_name="WEB_EXPERIMENTS",
            client_version="1",
            referer=REFERER_YOUTUBE,
        ),
        ClientContext(
            client_id=61,
            client_name="WEB_MUSIC",
            client_version="1.0",
            referer=REFERER_YOUTUBE_MUSIC,
        ),
        ClientContext(
            client_id=62,
            client_name="WEB_CREATOR",
            client_version="1.20241203.01.00",
            referer=REFERER_YOUTUBE_STUDIO,
            api_key="AIzaSyBUPetSUmoZL-OhlxA7wSac5XinrygCqMo",
        ),
        ClientContext(
            client_id=67,
            client_name="WEB_REMIX",
            client_version="1.20250219.01.00",
            referer=REFERER_YOUTUBE_MUSIC,
            api_key="AIzaSyC9XL3ZjWddXya6X74dJoCTL-WEYFDNX30",
        ),
        ClientContext(
            client_id=76,
            client_name="WEB_KIDS",
            client_version="2.20220414.00.00",
            referer=REFERER_YOUTUBE_KIDS,
            api_key="AIzaSyBbZV_fZ3an51sF-mvs5w37OqqbsTOzwtU",
        ),
        ClientContext(
            client_id=87,
            client_name="WEB_INTERNAL_ANALYTICS",
            client_version="0.1",
            referer=REFERER_YOUTUBE_ANALYTICS,
        ),
        ClientContext(
            client_id=88,
            client_name="WEB_PARENT_TOOLS",
            client_version="1.20220403",
        ),
    ],
)
