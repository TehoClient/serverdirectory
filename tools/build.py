"""Compile reviewed server submissions into the public CDN directory."""
import hashlib
import io
import json
import re
import warnings
from datetime import datetime
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
CDN = "https://serverdirectory.tehoclientcdn.com/servers/assets/"
HOST = re.compile(r"(?=.{1,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}$")

def require(condition, message):
    if not condition:
        raise ValueError(message)

def image_asset(folder, kind, output):
    files = [p for p in folder.iterdir() if p.stem == kind and p.suffix in (".png", ".gif")]
    require(len(files) == 1, f"{folder.name}: provide one {kind}.png or {kind}.gif")
    path = files[0]
    require(not path.is_symlink() and path.stat().st_size <= 5 * 1024 * 1024, f"Invalid {path}")
    data = path.read_bytes()
    with warnings.catch_warnings():
        warnings.simplefilter("error", Image.DecompressionBombWarning)
        with Image.open(io.BytesIO(data)) as im:
            require(im.format == ("PNG" if path.suffix == ".png" else "GIF"), "Image format mismatch")
            w, h = im.size
            require(128 <= w <= 1024 and w == h if kind == "logo" else 640 <= w <= 1920 and w * 9 == h * 16, f"Invalid {kind} dimensions: {w}x{h}")
            require(im.n_frames <= 120 and w * h * im.n_frames <= 150_000_000, "Animation too large")
            for frame in range(im.n_frames):
                im.seek(frame)
                im.load()
    name = hashlib.sha256(data).hexdigest() + path.suffix
    (output / name).write_bytes(data)
    return CDN + name

def build(root=ROOT):
    placements = json.loads((root / "placements.json").read_text("utf-8"))
    output = root / "dist" / "servers"
    assets = output / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    source = root / "listings"
    source.mkdir(exist_ok=True)
    rows, claimed = [], set()
    for folder in sorted(source.iterdir()):
        if folder.name == ".gitkeep" and folder.is_file() and not folder.is_symlink() and folder.stat().st_size == 0:
            continue
        require(folder.is_dir() and not folder.is_symlink() and re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", folder.name), "Invalid server folder")
        for path in folder.iterdir():
            require(not path.is_symlink() and path.is_file() and path.name in {"server.json", "logo.png", "logo.gif", "banner.png", "banner.gif"}, f"Unexpected file: {path}")
        metadata = folder / "server.json"
        require(metadata.stat().st_size <= 16384, "Metadata too large")
        row = json.loads(metadata.read_text("utf-8"))
        require(set(row) <= {"name", "address", "domains", "description"}, "Unknown metadata field (placement is maintainer-only)")
        require(isinstance(row.get("name"), str) and 1 <= len(row["name"]) <= 48, "Invalid name")
        require(isinstance(row.get("description", ""), str) and len(row.get("description", "")) <= 240, "Invalid description")
        require(all(ord(c) >= 32 for c in row["name"] + row.get("description", "")), "Control characters in text")
        domains = row.get("domains")
        require(isinstance(domains, list) and 1 <= len(domains) <= 16, "Invalid domains")
        for host in domains:
            require(isinstance(host, str) and HOST.fullmatch(host) and host not in claimed, f"Invalid or duplicate domain: {host}")
            claimed.add(host)
        address = row.get("address", "")
        require(isinstance(address, str), "Invalid address")
        parts = address.split(":")
        require(len(parts) <= 2 and parts[0] in domains and (len(parts) == 1 or parts[1].isdigit() and 1 <= int(parts[1]) <= 65535), "Address must belong to this listing")
        placement = placements.get(folder.name, {})
        require(set(placement) <= {"tier", "rank", "until"}, "Unknown placement field")
        tier = placement.get("tier", "community")
        require(tier in ("partnered", "sponsored", "community"), "Invalid placement")
        rank = placement.get("rank", 0)
        require(type(rank) is int and 0 <= rank <= 100000, "Invalid rank")
        until = placement.get("until")
        if tier == "sponsored":
            require(isinstance(until, str) and until.endswith("Z"), "Sponsorship requires UTC expiry")
            datetime.fromisoformat(until.replace("Z", "+00:00"))
        rows.append({**row, "id": folder.name, "tier": tier, "rank": rank, "sponsoredUntil": until,
                     "icon": image_asset(folder, "logo", assets), "banner": image_asset(folder, "banner", assets), "appId": None})
    require(set(placements) <= {r["id"] for r in rows}, "Placement references missing server")
    manifest = {"schemaVersion": 1, "brands": rows}
    temporary = output / "index.json.tmp"
    temporary.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", "utf-8")
    temporary.replace(output / "index.json")
    return manifest

if __name__ == "__main__":
    print(f"Built {len(build()['brands'])} server directory entries")
