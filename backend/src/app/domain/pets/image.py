IMAGE_HEADER_BYTES = 16

_JPEG = b"\xff\xd8\xff"
_PNG = b"\x89PNG\r\n\x1a\n"


def sniff_image_type(header: bytes) -> str | None:
    if header.startswith(_JPEG):
        return "image/jpeg"
    if header.startswith(_PNG):
        return "image/png"
    if len(header) >= 12 and header[:4] == b"RIFF" and header[8:12] == b"WEBP":
        return "image/webp"
    return None
