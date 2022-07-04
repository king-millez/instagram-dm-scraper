from distutils.command.config import config
import json
import requests  # type: ignore

from os import path
from typing import Dict

from igdm.ig_requests import ig_get, ig_head
from igdm.config import conf


_REQUIRED = ["sessionid"]


def _generate_cookies(*args, **kwargs) -> None:
    _cookies = {}

    if args:
        for cookie in args[0].split("; "):
            key, value = cookie.split("=")
            if key in _REQUIRED:
                _cookies[key] = value

    for required_cookie in _REQUIRED:
        if required_cookie in kwargs.keys():
            _cookies[required_cookie] = kwargs[required_cookie]
        elif required_cookie not in _cookies.keys():
            _cookies[required_cookie] = input(
                f"Input the value for {required_cookie}: "
            )

    with open(conf.creds_json, "w") as f:
        f.write(json.dumps(_cookies))


def _test_cookies(cookies: Dict[str, str | int]) -> bool:
    try:
        ig_get("https://i.instagram.com/api/v1/direct_v2/inbox/", cookies=cookies)
    except requests.exceptions.TooManyRedirects:
        print("Bad session ID")

        with open(conf.creds_json, "w") as f:
            f.write("")

        _generate_cookies()

        return False

    except Exception:
        return False

    return True


if path.isfile(conf.creds_json):
    with open(conf.creds_json, "r") as f:
        try:
            json.loads(f.read())
        except json.decoder.JSONDecodeError:
            _generate_cookies()
else:
    _generate_cookies()


_valid_cookies = False
while not _valid_cookies:
    with open(conf.creds_json, "r") as f:
        _valid_cookies = _test_cookies(json.loads(f.read()))

with open(conf.creds_json, "r") as f:
    cookies = json.loads(f.read())
