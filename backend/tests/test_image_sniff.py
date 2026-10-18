import pytest

from app.domain.pets.image import sniff_image_type

JPEG = b"\xff\xd8\xff\xe0" + b"\x00" * 12
PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 8
WEBP = b"RIFF" + b"\x00\x00\x00\x00" + b"WEBP" + b"VP8 "


@pytest.mark.parametrize(
    ("header", "media_type"),
    [
        (b"\xff\xd8\xff", "image/jpeg"),
        (JPEG, "image/jpeg"),
        (b"\x89PNG\r\n\x1a\n", "image/png"),
        (PNG, "image/png"),
        (b"RIFF\x00\x00\x00\x00WEBP", "image/webp"),
        (WEBP, "image/webp"),
    ],
)
def test_sniff_recognizes_jpeg_png_and_webp(header, media_type):
    assert sniff_image_type(header) == media_type


def test_sniff_does_not_confuse_formats():
    assert sniff_image_type(JPEG) != "image/png"
    assert sniff_image_type(PNG) != "image/jpeg"
    assert sniff_image_type(WEBP) != "image/jpeg"
    assert sniff_image_type(b"RIFF" + b"\x00\x00\x00\x00" + b"WAVE" + b"fmt ") is None
    assert sniff_image_type(b"not an image!!!!") is None


@pytest.mark.parametrize(
    "header",
    [b"", b"\xff", b"\xff\xd8", b"\x89PNG", b"RIFF", b"RIFF\x00\x00\x00\x00WEB"],
)
def test_short_or_empty_headers_are_not_images(header):
    assert sniff_image_type(header) is None
