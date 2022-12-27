
import requests
from requests.models import Response

from src.safe_url.pass_captcha import PassCaptcha


def safe_get_url(url: str) -> Response:
    # open with GET method
    resp = requests.get(url)
    # Caso 429: too many requests
    if resp.status_code == 429:
        return PassCaptcha(url)
    else:
        return resp
