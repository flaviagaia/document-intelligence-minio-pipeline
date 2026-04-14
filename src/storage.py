from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

try:
    from minio import Minio
except Exception:  # pragma: no cover - optional dependency runtime issue
    Minio = None


ROOT_DIR = Path(__file__).resolve().parents[1]
LOCAL_OBJECT_ROOT = ROOT_DIR / "data" / "object_store"


@dataclass
class StoredObject:
    bucket: str
    object_name: str
    payload: str


class LocalObjectStore:
    def __init__(self, root_dir: Path | None = None) -> None:
        self.root_dir = root_dir or LOCAL_OBJECT_ROOT
        self.root_dir.mkdir(parents=True, exist_ok=True)

    def put_text(self, bucket: str, object_name: str, payload: str) -> None:
        target = self.root_dir / bucket / object_name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(payload, encoding="utf-8")

    def list_objects(self, bucket: str) -> List[str]:
        bucket_dir = self.root_dir / bucket
        if not bucket_dir.exists():
            return []
        return sorted(
            str(path.relative_to(bucket_dir))
            for path in bucket_dir.rglob("*")
            if path.is_file()
        )

    def read_text(self, bucket: str, object_name: str) -> str:
        return (self.root_dir / bucket / object_name).read_text(encoding="utf-8")


class MinioObjectStore:
    def __init__(self) -> None:
        endpoint = os.getenv("MINIO_ENDPOINT")
        access_key = os.getenv("MINIO_ACCESS_KEY")
        secret_key = os.getenv("MINIO_SECRET_KEY")
        secure = os.getenv("MINIO_SECURE", "false").lower() == "true"
        if not (endpoint and access_key and secret_key and Minio):
            raise RuntimeError("MinIO runtime not configured.")

        self.client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure,
        )

    def ensure_bucket(self, bucket: str) -> None:
        if not self.client.bucket_exists(bucket):
            self.client.make_bucket(bucket)

    def put_text(self, bucket: str, object_name: str, payload: str) -> None:
        import io

        self.ensure_bucket(bucket)
        content = payload.encode("utf-8")
        self.client.put_object(
            bucket,
            object_name,
            io.BytesIO(content),
            length=len(content),
            content_type="application/json",
        )

    def list_objects(self, bucket: str) -> List[str]:
        self.ensure_bucket(bucket)
        return sorted(obj.object_name for obj in self.client.list_objects(bucket, recursive=True))


def resolve_store() -> tuple[str, object]:
    try:
        return "minio_s3_api", MinioObjectStore()
    except Exception:
        return "local_filesystem_fallback", LocalObjectStore()


def as_json(payload: Dict[str, object]) -> str:
    return json.dumps(payload, indent=2, ensure_ascii=True)
