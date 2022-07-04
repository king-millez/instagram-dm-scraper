import requests  # type: ignore

from typing import Dict


IG_HEADERS = {
    "Host": "i.instagram.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0",
    "X-IG-App-ID": "936619743392459",
}


def ig_get(url, cookies: Dict[str, str | int]):
    return requests.get(url, cookies=cookies, headers=IG_HEADERS)


def ig_head(url, cookies: Dict[str, str | int]):
    return requests.head(url, cookies=cookies, headers=IG_HEADERS)
