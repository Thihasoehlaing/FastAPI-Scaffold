import boto3
from typing import BinaryIO, Dict, Any
from app.config.settings import settings

class S3Storage:
    provider = "s3"

    def __init__(self):
        kwargs = {}
        if settings.S3_ENDPOINT_URL:
            kwargs["endpoint_url"] = settings.S3_ENDPOINT_URL
        if settings.S3_ACCESS_KEY and settings.S3_SECRET_KEY:
            kwargs["aws_access_key_id"] = settings.S3_ACCESS_KEY
            kwargs["aws_secret_access_key"] = settings.S3_SECRET_KEY
        if settings.S3_REGION:
            kwargs["region_name"] = settings.S3_REGION
        self.client = boto3.client("s3", **kwargs)
        self.bucket = settings.S3_BUCKET
        self.region = settings.S3_REGION
        self.endpoint_url = settings.S3_ENDPOINT_URL

    async def upload(self, *, key: str, body: BinaryIO, content_type: str) -> None:
        extra = {"ContentType": content_type}
        # For public objects, caller should set is_public True and use presign or set ACL after upload if desired.
        self.client.upload_fileobj(Fileobj=body, Bucket=self.bucket, Key=key, ExtraArgs=extra)

    async def delete(self, *, key: str) -> None:
        self.client.delete_object(Bucket=self.bucket, Key=key)

    def _http_object_url(self, key: str) -> str:
        if self.endpoint_url:  # e.g., DO Spaces / R2 custom endpoint
            base = self.endpoint_url.rstrip("/")
            # path-style works across providers
            return f"{base}/{self.bucket}/{key}"
        # AWS default virtual-hosted style
        return f"https://{self.bucket}.s3.{self.region}.amazonaws.com/{key}"

    def url(self, *, key: str, is_public: bool = False, ttl_seconds: int = 900) -> str:
        if is_public and self.endpoint_url:
            return self._http_object_url(key)
        if is_public and not self.endpoint_url:
            return self._http_object_url(key)
        # private → presigned GET
        return self.presign_get(key=key, expires_in=ttl_seconds)

    def presign_get(self, *, key: str, expires_in: int = 900) -> str:
        return self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=expires_in,
        )

    def presign_post(self, *, key: str, content_type: str, is_public: bool = False, expires_in: int = 900) -> Dict[str, Any]:
        fields = {"Content-Type": content_type}
        conditions: list = [{"Content-Type": content_type}]
        if is_public:
            fields["acl"] = "public-read"
            conditions.append({"acl": "public-read"})

        resp = self.client.generate_presigned_post(
            Bucket=self.bucket,
            Key=key,
            Fields=fields,
            Conditions=conditions,
            ExpiresIn=expires_in,
        )
        # resp = {"url": "...", "fields": {...}}
        return resp
