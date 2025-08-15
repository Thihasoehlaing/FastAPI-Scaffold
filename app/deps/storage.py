from app.config.settings import settings
from app.services.storage.local_storage import LocalStorage
from app.services.storage.s3_storage import S3Storage
from app.services.storage.azure_blob_storage import AzureBlobStorage

def get_storage():
    driver = settings.STORAGE_DRIVER.lower()
    if driver == "local":
        return LocalStorage()
    if driver == "s3":
        return S3Storage()
    if driver == "azure":
        return AzureBlobStorage()
    raise RuntimeError(f"Unsupported STORAGE_DRIVER={settings.STORAGE_DRIVER}")