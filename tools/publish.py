"""Publish the directory from trusted main, never with secrets in a PR."""
import os
import re
from pathlib import Path
from urllib.request import Request, build_opener, HTTPRedirectHandler

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None

def publish():
    host = os.environ.get("BUNNY_STORAGE_HOST") or "storage.bunnycdn.com"
    zone = os.environ["BUNNY_STORAGE_ZONE"]
    key = os.environ["BUNNY_STORAGE_KEY"]
    if not re.fullmatch(r"(?:[a-z]+\.)?storage\.bunnycdn\.com", host) or not re.fullmatch(r"[a-zA-Z0-9_-]+", zone):
        raise ValueError("Invalid storage host or zone")
    root = Path(__file__).resolve().parent.parent / "dist"
    files = sorted((root / "servers" / "assets").iterdir()) + [root / "servers" / "index.json"]
    opener = build_opener(NoRedirect())
    for path in files:
        mime = {".png": "image/png", ".gif": "image/gif", ".json": "application/json"}[path.suffix]
        request = Request(f"https://{host}/{zone}/{path.relative_to(root).as_posix()}", data=path.read_bytes(), method="PUT", headers={"AccessKey": key, "Content-Type": mime})
        with opener.open(request, timeout=60) as response:
            if not 200 <= response.status < 300:
                raise RuntimeError("CDN upload failed")
        print(f"Uploaded {path.relative_to(root)}")

if __name__ == "__main__":
    publish()
