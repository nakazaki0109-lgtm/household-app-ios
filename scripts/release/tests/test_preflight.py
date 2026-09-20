import json
import struct
import zlib

from scripts.release import preflight


def make_png(path, width, height, color_type=2):
    def chunk(kind, data):
        body = kind + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body))

    ihdr = struct.pack(">IIBBBBB", width, height, 8, color_type, 0, 0, 0)
    path.write_bytes(preflight.PNG_SIGNATURE + chunk(b"IHDR", ihdr) + chunk(b"IEND", b""))


def write_contents(icon_dir, filename=None):
    image = {"idiom": "universal", "platform": "ios", "size": "1024x1024"}
    if filename:
        image["filename"] = filename
    (icon_dir / "Contents.json").write_text(json.dumps({"images": [image]}))


def test_icon_missing_when_no_filename_registered(tmp_path):
    write_contents(tmp_path)
    problems = preflight.check_icon(tmp_path)
    assert len(problems) == 1
    assert "AppIcon.appiconset" in problems[0]


def test_icon_registered_but_file_absent(tmp_path):
    write_contents(tmp_path, "AppIcon.png")
    assert "AppIcon.png がありません" in preflight.check_icon(tmp_path)[0]


def test_valid_icon_passes(tmp_path):
    write_contents(tmp_path, "AppIcon.png")
    make_png(tmp_path / "AppIcon.png", 1024, 1024)
    assert preflight.check_icon(tmp_path) == []


def test_wrong_size_icon_fails(tmp_path):
    write_contents(tmp_path, "AppIcon.png")
    make_png(tmp_path / "AppIcon.png", 512, 512)
    assert "512x512" in preflight.check_icon(tmp_path)[0]


def test_icon_with_alpha_fails(tmp_path):
    write_contents(tmp_path, "AppIcon.png")
    make_png(tmp_path / "AppIcon.png", 1024, 1024, color_type=6)
    assert "透過" in preflight.check_icon(tmp_path)[0]


def test_non_png_icon_fails(tmp_path):
    write_contents(tmp_path, "AppIcon.png")
    (tmp_path / "AppIcon.png").write_bytes(b"not a png at all, just some bytes here")
    assert "PNG ではありません" in preflight.check_icon(tmp_path)[0]


def test_contact_file_missing(tmp_path):
    problems = preflight.check_review_contact(tmp_path / "c.json", tmp_path / "example.json")
    assert "store/review_contact.local.json がありません" in problems[0]


def test_contact_blank_fields_are_listed(tmp_path):
    contact = tmp_path / "c.json"
    contact.write_text(json.dumps({"first_name": "太郎", "last_name": "", "phone_number": " ", "email_address": "a@b.c"}))
    problems = preflight.check_review_contact(contact, tmp_path / "example.json")
    assert len(problems) == 2
    assert any("last_name" in p for p in problems)
    assert any("phone_number" in p for p in problems)


def test_complete_contact_passes(tmp_path):
    contact = tmp_path / "c.json"
    contact.write_text(json.dumps({"first_name": "a", "last_name": "b", "phone_number": "1", "email_address": "c"}))
    assert preflight.check_review_contact(contact, tmp_path / "example.json") == []


def test_urls_blank_and_invalid(tmp_path):
    (tmp_path / "privacy_url.txt").write_text("")
    (tmp_path / "support_url.txt").write_text("example.com")
    problems = preflight.check_urls(tmp_path)
    assert "privacy_url — store/metadata/ja/privacy_url.txt に URL を1行で入力してください" in problems
    assert any("support_url" in p and "http(s)://" in p for p in problems)


def test_urls_valid(tmp_path):
    (tmp_path / "privacy_url.txt").write_text("https://example.com/privacy\n")
    (tmp_path / "support_url.txt").write_text("https://example.com/support\n")
    assert preflight.check_urls(tmp_path) == []
