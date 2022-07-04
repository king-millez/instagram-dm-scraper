from dataclasses import dataclass


@dataclass(frozen=True)
class _Config:
    creds_json: str = "igdm/credentials/cookies.json"


conf = _Config()
