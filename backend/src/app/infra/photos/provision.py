"""Provision a private bucket and a restricted application user before API startup."""

import asyncio
import json
from urllib.parse import urlencode

import httpx
from botocore.auth import S3SigV4Auth
from botocore.awsrequest import AWSRequest
from botocore.credentials import Credentials
from botocore.exceptions import ClientError

from app.bootstrap import build_container
from app.infra.config import RustFSAdminConfig, S3Config
from app.infra.photos.s3 import create_s3_client


async def provision(config: S3Config, root_access_key: str, root_secret_key: str) -> None:
    if not root_access_key or not root_secret_key or root_access_key == config.access_key:
        raise ValueError("RustFS requires separate, non-empty administrator and application credentials")
    root_config = config.model_copy(update={"access_key": root_access_key, "secret_key": root_secret_key})
    async with create_s3_client(root_config) as client:
        try:
            await client.head_bucket(Bucket=config.bucket)
        except ClientError as error:
            if str(error.response["Error"]["Code"]) not in {"404", "NoSuchBucket", "NotFound"}:
                raise
            kwargs = {"Bucket": config.bucket}
            if config.region != "us-east-1":
                kwargs["CreateBucketConfiguration"] = {"LocationConstraint": config.region}
            await client.create_bucket(**kwargs)

    policy_name = f"{config.bucket}-photos"
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"],
                "Resource": [f"arn:aws:s3:::{config.bucket}/pets/*"],
            },
        ],
    }
    credentials = Credentials(root_access_key, root_secret_key)
    async with httpx.AsyncClient(timeout=15, trust_env=False) as http:

        async def admin(path: str, params: dict[str, str], body: dict | None = None) -> None:
            url = f"{config.endpoint_url}/rustfs/admin/v3/{path}?{urlencode(params)}"
            data = json.dumps(body).encode() if body is not None else b""
            request = AWSRequest(method="PUT", url=url, data=data, headers={"Content-Type": "application/json"})
            S3SigV4Auth(credentials, "s3", config.region).add_auth(request)
            response = await http.put(url, content=data, headers=dict(request.headers))
            if not response.is_success:
                raise RuntimeError(f"RustFS provisioning failed at {path}: HTTP {response.status_code}")

        await admin("add-canned-policy", {"name": policy_name}, policy)
        await admin("add-user", {"accessKey": config.access_key}, {"secretKey": config.secret_key, "status": "enabled"})
        await admin(
            "set-user-or-group-policy",
            {"policyName": policy_name, "userOrGroup": config.access_key, "isGroup": "false"},
        )


async def main() -> None:
    container = build_container()
    try:
        admin_config = await container.get(RustFSAdminConfig)
        await provision(
            await container.get(S3Config),
            admin_config.access_key,
            admin_config.secret_key,
        )
    finally:
        await container.close()


if __name__ == "__main__":
    asyncio.run(main())
