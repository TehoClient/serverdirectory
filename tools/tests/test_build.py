import json
import tempfile
import unittest
import sys
from pathlib import Path
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from build import build

class DirectoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "placements.json").write_text("{}")
        self.server = self.root / "listings" / "example"
        self.server.mkdir(parents=True)
        self.metadata = {"name": "Example", "address": "play.example.com", "domains": ["play.example.com"]}
        self.write()
        Image.new("RGBA", (128, 128)).save(self.server / "logo.png")
        Image.new("RGB", (640, 360)).save(self.server / "banner.png")

    def write(self):
        (self.server / "server.json").write_text(json.dumps(self.metadata))

    def test_community_and_hashed_assets(self):
        row = build(self.root)["brands"][0]
        self.assertEqual(row["tier"], "community")
        self.assertIsNone(row["appId"])
        self.assertRegex(row["icon"], r"/servers/assets/[a-f0-9]{64}\.png$")
        self.assertTrue(row["icon"].startswith("https://serverdirectory.tehoclientcdn.com/"))
        self.assertTrue(row["banner"].startswith("https://serverdirectory.tehoclientcdn.com/"))

    def test_no_self_promotion(self):
        self.metadata["tier"] = "partnered"
        self.write()
        with self.assertRaises(ValueError): build(self.root)

    def test_listing_marker_and_cdn_layout(self):
        (self.root / "listings" / ".gitkeep").touch()
        manifest = build(self.root)
        self.assertEqual(len(manifest["brands"]), 1)
        self.assertEqual(json.loads((self.root / "dist" / "servers" / "index.json").read_text()), manifest)
        self.assertFalse((self.root / "servers").exists())

    def test_nonempty_listing_marker_rejected(self):
        (self.root / "listings" / ".gitkeep").write_text("unexpected content")
        with self.assertRaises(ValueError): build(self.root)

    def test_address_ownership(self):
        self.metadata["address"] = "other.example.com"
        self.write()
        with self.assertRaises(ValueError): build(self.root)

    def test_expiry_required(self):
        (self.root / "placements.json").write_text('{"example":{"tier":"sponsored"}}')
        with self.assertRaises(ValueError): build(self.root)

    def test_invalid_dimensions(self):
        Image.new("RGB", (640, 640)).save(self.server / "banner.png")
        with self.assertRaises(ValueError): build(self.root)

    def test_animated_gif(self):
        (self.server / "logo.png").unlink()
        Image.new("RGB", (128, 128), "red").save(self.server / "logo.gif", save_all=True, append_images=[Image.new("RGB", (128, 128), "blue")], duration=100, loop=0)
        self.assertTrue(build(self.root)["brands"][0]["icon"].endswith(".gif"))

    def test_path_traversal_file(self):
        (self.server / "script.py").write_text("print('not allowed')")
        with self.assertRaises(ValueError): build(self.root)

if __name__ == "__main__":
    unittest.main()
