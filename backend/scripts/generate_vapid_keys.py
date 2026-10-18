"""Print VAPID keys for VAPID_PUBLIC_KEY / VAPID_PRIVATE_KEY.

Run from backend/: `uv run python scripts/generate_vapid_keys.py`.
The public key is the uncompressed P-256 point, base64url, for pushManager.subscribe.
The private key is the raw 32-byte scalar, base64url, which pywebpush accepts.
"""

from cryptography.hazmat.primitives import serialization
from py_vapid import Vapid
from py_vapid.utils import b64urlencode


def main() -> None:
    vapid = Vapid()
    vapid.generate_keys()
    private = vapid.private_key.private_numbers().private_value.to_bytes(32, "big")
    public = vapid.public_key.public_bytes(serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint)
    print(f"VAPID_PUBLIC_KEY={b64urlencode(public)}")  # noqa: T201
    print(f"VAPID_PRIVATE_KEY={b64urlencode(private)}")  # noqa: T201
    print("VAPID_SUBJECT=mailto:admin@example.com")  # noqa: T201


if __name__ == "__main__":
    main()
