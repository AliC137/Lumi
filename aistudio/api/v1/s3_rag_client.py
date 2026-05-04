"""Shared S3 client + bucket for RAG uploads, listing, and downloads."""

from functools import lru_cache
import logging
import os

import boto3

logger = logging.getLogger(__name__)


def _legacy_s3_from_env():
    """Match older ``rag_upload`` defaults when ``s3.env`` / ``S3Config`` is unavailable."""
    endpoint = os.getenv("AWS_S3_ENDPOINT", "https://storage.yandexcloud.net")
    bucket = os.getenv("AWS_BUCKET_NAME", "aistudio")
    region = os.getenv("AWS_DEFAULT_REGION", "ru-central1")
    key = os.getenv("AWS_ACCESS_KEY_ID")
    secret = os.getenv("AWS_SECRET_ACCESS_KEY")
    kw = {"endpoint_url": endpoint, "region_name": region}
    if key and secret:
        kw["aws_access_key_id"] = key
        kw["aws_secret_access_key"] = secret
    return boto3.client("s3", **kw), bucket


@lru_cache(maxsize=1)
def get_s3_client_and_bucket():
    """Prefer ``S3Config`` (``s3.env``); fall back to env vars + Yandex defaults like legacy code."""
    try:
        from aistudio.config.config import S3Config

        c = S3Config()
        client = boto3.client(
            "s3",
            endpoint_url=c.AWS_S3_ENDPOINT,
            region_name=c.AWS_DEFAULT_REGION,
            aws_access_key_id=c.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=c.AWS_SECRET_ACCESS_KEY,
        )
        return client, c.AWS_BUCKET_NAME
    except Exception as e:
        logger.warning("S3Config unavailable (%s); using legacy env / default bucket.", e)
        return _legacy_s3_from_env()
