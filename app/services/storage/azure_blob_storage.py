from datetime import datetime, timedelta
from typing import BinaryIO, Dict, Any, Optional
from urllib.parse import urlencode

from azure.storage.blob import (
    BlobServiceClient,
    generate_blob_sas,
    BlobSasPermissions,
    ContentSettings,
)
from app.config.settings import settings


class AzureBlobStorage:
    provider = "azure"

    def __init__(self):
        if not settings.AZURE_BLOB_CONNECTION_STRING or not settings.AZURE_CONTAINER:
            raise RuntimeError("Azure storage not configured (connection string / container missing)")
        self.container = settings.AZURE_CONTAINER
        self.bsc = BlobServiceClient.from_connection_string(settings.AZURE_BLOB_CONNECTION_STRING)
        self.container_client = self.bsc.get_container_client(self.container)

        # Parse account info for URL building
        self.account_name = self.bsc.account_name
        # Default endpoint pattern; if using custom domains, expose via CDN and set PUBLIC_BASE_URL.
        self.blob_base = f"https://{self.account_name}.blob.core.windows.net/{self.container}"

    async def upload(self, *, key: str, body: BinaryIO, content_type: str) -> None:
        blob = self.container_client.get_blob_client(key)
        # overwrite=True to allow idempotent re-uploads of same key if needed
        blob.upload_blob(
            data=body,
            overwrite=True,
            content_settings=ContentSettings(content_type=content_type),
        )

    async def delete(self, *, key: str) -> None:
        blob = self.container_client.get_blob_client(key)
        blob.delete_blob(delete_snapshots="include")

    def url(self, *, key: str, is_public: bool = False, ttl_seconds: int = 900) -> str:
        # If using a public container or fronted by CDN, you can return direct URL
        # Otherwise, return a signed (read) SAS URL.
        if is_public and settings.PUBLIC_BASE_URL:
            base = settings.PUBLIC_BASE_URL.rstrip("/")
            return f"{base}/{key}"
        if is_public:
            return f"{self.blob_base}/{key}"
        return self.presign_get(key=key, expires_in=ttl_seconds)

    def _sas_token(
        self,
        *,
        key: str,
        permissions: BlobSasPermissions,
        expires_in: int,
        content_type: Optional[str] = None,
    ) -> str:
        expiry = datetime.utcnow() + timedelta(seconds=expires_in)
        sas = generate_blob_sas(
            account_name=self.account_name,
            container_name=self.container,
            blob_name=key,
            account_key=self.bsc.credential.account_key,  # uses shared key from connection string
            permission=permissions,
            expiry=expiry,
            content_type=content_type,
        )
        return sas

    def presign_get(self, *, key: str, expires_in: int = 900) -> str:
        sas = self._sas_token(key=key, permissions=BlobSasPermissions(read=True), expires_in=expires_in)
        return f"{self.blob_base}/{key}?{sas}"

    def presign_put(self, *, key: str, content_type: str, is_public: bool = False, expires_in: int = 900) -> Dict[str, Any]:
        # Azure commonly uses a SAS URL for PUT/POST from the client (no form fields needed)
        # Client performs: PUT <url-with-sas> with header "x-ms-blob-type: BlockBlob" and "Content-Type"
        sas = self._sas_token(
            key=key,
            permissions=BlobSasPermissions(write=True, create=True),
            expires_in=expires_in,
            content_type=content_type,
        )
        url = f"{self.blob_base}/{key}?{sas}"
        fields = {
            "x-ms-blob-type": "BlockBlob",
            "Content-Type": content_type,
            # If you need public access post-upload, set container to public or run a follow-up ACL step server-side.
        }
        return {"url": url, "fields": fields}
