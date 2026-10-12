"""
    RTP account (conta.rtp.pt) login and the per-user RTP Play data the website
    keeps for it: favourites ("Os seus favoritos") and continue watching.

    Login uses the OAuth device flow, so the password is only ever typed on
    RTP's own login page and Kodi just keeps the tokens.
"""

import base64
import json
import os
import time

import requests

SSO_URL = "https://conta.rtp.pt/realms/rtp/protocol/openid-connect"
CLIENT_ID = "rtp"
API_URL = "https://p9194zb7ga.execute-api.eu-west-1.amazonaws.com/prod"
PROJECT = "play"


class LoginError(Exception):
    pass


def _jwt_payload(token):
    payload = token.split(".")[1]
    return json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))


def _items(response):
    """The API returns either a list of entries or a dict keyed by entry key."""
    if isinstance(response, dict):
        if isinstance(response.get("Items"), list):
            return response["Items"]
        return [v for v in response.values() if isinstance(v, dict)]
    return response if isinstance(response, list) else []


class Account:
    def __init__(self, profile_dir):
        self.path = os.path.join(profile_dir, "account.json")
        self.tokens = {}
        try:
            with open(self.path) as f:
                self.tokens = json.load(f)
        except (OSError, ValueError):
            pass

    def _save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w") as f:
            json.dump(self.tokens, f)
        os.chmod(self.path, 0o600)

    @property
    def logged_in(self):
        return bool(self.tokens.get("refresh_token"))

    @property
    def username(self):
        if not self.tokens.get("access_token"):
            return ""
        claims = _jwt_payload(self.tokens["access_token"])
        return claims.get("name") or claims.get("preferred_username") or claims.get("email", "")

    def logout(self):
        refresh = self.tokens.get("refresh_token")
        if refresh:
            try:
                requests.post(SSO_URL + "/logout", data={"client_id": CLIENT_ID, "refresh_token": refresh}, timeout=10)
            except requests.RequestException:
                pass
        self.tokens = {}
        try:
            os.remove(self.path)
        except OSError:
            pass

    # Device flow

    def start_device_login(self):
        """:return: dict with device_code, user_code, verification_uri(_complete), expires_in and interval"""
        r = requests.post(SSO_URL + "/auth/device",
                          data={"client_id": CLIENT_ID, "scope": "openid offline_access"}, timeout=20)
        r.raise_for_status()
        return r.json()

    def poll_device_login(self, device_code):
        """:return: True once logged in, False while still waiting for the user"""
        r = requests.post(SSO_URL + "/token", data={
            "client_id": CLIENT_ID,
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            "device_code": device_code,
        }, timeout=20)
        data = r.json()
        if "access_token" in data:
            self._store(data)
            return True
        if data.get("error") in ("authorization_pending", "slow_down"):
            return False
        raise LoginError(data.get("error_description") or data.get("error") or "login failed")

    def _store(self, data):
        self.tokens = {
            "access_token": data["access_token"],
            "refresh_token": data.get("refresh_token", self.tokens.get("refresh_token")),
            "expires_at": time.time() + int(data.get("expires_in", 300)),
        }
        self._save()

    def access_token(self):
        if not self.logged_in:
            return None
        if self.tokens.get("expires_at", 0) - time.time() > 60:
            return self.tokens["access_token"]
        r = requests.post(SSO_URL + "/token", data={
            "client_id": CLIENT_ID,
            "grant_type": "refresh_token",
            "refresh_token": self.tokens["refresh_token"],
        }, timeout=20)
        data = r.json()
        if "access_token" not in data:
            # The session was revoked or expired; the user has to log in again
            self.tokens = {}
            self._save()
            return None
        self._store(data)
        return self.tokens["access_token"]

    # RTP Play user data

    def _request(self, method, path, body=None):
        token = self.access_token()
        if not token:
            raise LoginError("not logged in")
        profile_id = _jwt_payload(token)["sub"] + "-0"
        if body is not None:
            body = dict(body, profile_id=profile_id)
        r = requests.request(method, API_URL + path, json=body, timeout=20, headers={
            "Authorization": "Bearer " + token,
            "profile_id": profile_id,
        })
        r.raise_for_status()
        return r.json() if r.content else None

    def get_favorites(self):
        favorites = _items(self._request("GET", "/favorites/" + PROJECT))
        return sorted(favorites, key=lambda f: f.get("timestamp") or 0, reverse=True)

    def add_favorite(self, favorite):
        favorite = dict(favorite, project=PROJECT, timestamp=int(time.time() * 1000))
        self._request("POST", "/favorites", {"favorite": favorite})

    def remove_favorite(self, favorite):
        self._request("DELETE", "/favorites", {"favorite": dict(favorite, project=PROJECT)})

    def get_watching(self):
        """Latest unfinished episode per program, most recent first (as the website shows it)."""
        latest = {}
        for entry in _items(self._request("GET", "/watching/" + PROJECT)):
            if str(entry.get("ended", 0)) == "1":
                continue
            program = str(entry.get("program_id", ""))
            if program not in latest or (entry.get("timestamp") or 0) > (latest[program].get("timestamp") or 0):
                latest[program] = entry
        return sorted(latest.values(), key=lambda e: e.get("timestamp") or 0, reverse=True)

    def get_progress(self, key, program_id):
        """Saved position of one episode in milliseconds, or 0."""
        for entry in _items(self._request("GET", "/watch/{}/{}".format(key, program_id))):
            if str(entry.get("key")) == str(key) and str(entry.get("ended", 0)) != "1":
                return int(float(entry.get("progress") or 0))
        return 0

    def update_watching(self, telemetry, position_ms):
        entry = dict(telemetry, project=PROJECT, ended=0, timestamp=int(time.time() * 1000),
                     progress=position_ms,
                     progress_complete=position_ms + 1000 * int(telemetry.get("content_duration_before") or 0))
        self._request("POST", "/telemetry", entry)

    def ended_watching(self, telemetry):
        entry = dict(telemetry, project=PROJECT, ended=1, timestamp=int(time.time() * 1000))
        self._request("POST", "/ended", entry)
