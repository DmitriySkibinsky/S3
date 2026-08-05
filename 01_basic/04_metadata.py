"""
S3 Metadata Lab
---------------
Показывает:
1. Подключение к MinIO/S3
2. Загрузку файла с system + user metadata
3. Чтение метаданных
4. Изменение метаданных
5. Копирование с сохранением и заменой метаданных
"""

import os
from datetime import datetime
from pathlib import Path

import boto3
from botocore.client import Config


# ====================== НАСТРОЙКИ ======================
ENDPOINT = "http://localhost:9000"

BUCKET = f"metadata-lab-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
LOCAL_FILE = Path("./template_data/S3_img.png")
# =======================================================


def get_client():
    return boto3.client(
    "s3",
        endpoint_url="http://localhost:9000",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name="us-east-1",
    )


def print_header(title: str):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def show_metadata(s3, bucket: str, key: str):
    resp = s3.head_object(Bucket=bucket, Key=key)
    print(f"\nKey: {key}")
    print(f"  Content-Type  : {resp.get('ContentType')}")
    print(f"  Size          : {resp.get('ContentLength')}")
    print(f"  ETag          : {resp.get('ETag')}")
    print(f"  Last-Modified : {resp.get('LastModified')}")
    print(f"  User metadata : {resp.get('Metadata', {})}")


def main():
    s3 = get_client()

    # ---------- 0. Проверка локального файла ----------
    if not LOCAL_FILE.exists():
        LOCAL_FILE.parent.mkdir(parents=True, exist_ok=True)
        LOCAL_FILE.write_bytes(b"fake image data for metadata lab")
        print(f"Создан тестовый файл: {LOCAL_FILE}")

    # ---------- 1. Создаём бакет ----------
    print_header("1. Создание бакета")
    try:
        s3.create_bucket(Bucket=BUCKET)
        print(f"Бакет создан: {BUCKET}")
    except s3.exceptions.BucketAlreadyOwnedByYou:
        print(f"Бакет уже существует: {BUCKET}")

    # ---------- 2. Загрузка через upload_file ----------
    print_header("2. Загрузка через upload_file (system + user metadata)")

    key_upload = "documents/2026/report.png"

    s3.upload_file(
        Filename=str(LOCAL_FILE),
        Bucket=BUCKET,
        Key=key_upload,
        ExtraArgs={
            # system metadata
            "ContentType": "image/png",
            "ContentDisposition": "inline",
            "CacheControl": "max-age=3600",
            # user metadata (только ASCII)
            "Metadata": {
                "author": "Ivan",
                "project": "lab",
                "status": "draft",
                "department": "backend",
            },
        },
    )
    print(f"Загружен: s3://{BUCKET}/{key_upload}")
    show_metadata(s3, BUCKET, key_upload)

    # ---------- 2b. Загрузка через put_object ----------
    print_header("2b. Загрузка через put_object")

    key_put = "documents/2026/report-put.png"

    with open(LOCAL_FILE, "rb") as f:
        s3.put_object(
            Bucket=BUCKET,
            Key=key_put,
            Body=f,
            ContentType="image/png",
            Metadata={
                "author": "Ivan",
                "project": "lab",
                "status": "draft",
                "upload_method": "put_object",
            },
        )
    print(f"Загружен: s3://{BUCKET}/{key_put}")
    show_metadata(s3, BUCKET, key_put)

    # ---------- 3. Чтение метаданных ----------
    print_header("3. Чтение метаданных (head_object)")
    show_metadata(s3, BUCKET, key_upload)

    # ---------- 4. Изменение только метаданных ----------
    print_header("4. Изменение метаданных (copy сам в себя + REPLACE)")

    s3.copy_object(
        Bucket=BUCKET,
        Key=key_upload,
        CopySource={"Bucket": BUCKET, "Key": key_upload},
        Metadata={
            "author": "Petr",
            "project": "lab",
            "status": "reviewed",
            "reviewed_by": "admin",
        },
        MetadataDirective="REPLACE",
        ContentType="image/png",
    )
    print("Метаданные обновлены")
    show_metadata(s3, BUCKET, key_upload)

    # ---------- 5. Копирование с сохранением метаданных ----------
    print_header("5a. Копирование с СОХРАНЕНИЕМ метаданных")

    key_copy_keep = "archive/report.png"

    s3.copy_object(
        Bucket=BUCKET,
        Key=key_copy_keep,
        CopySource={"Bucket": BUCKET, "Key": key_upload},
        # MetadataDirective по умолчанию = COPY
    )
    print(f"Скопирован → {key_copy_keep}")
    show_metadata(s3, BUCKET, key_copy_keep)

    # ---------- 5b. Копирование с заменой метаданных ----------
    print_header("5b. Копирование с ЗАМЕНОЙ метаданных")

    key_copy_replace = "archive/report-final.png"

    s3.copy_object(
        Bucket=BUCKET,
        Key=key_copy_replace,
        CopySource={"Bucket": BUCKET, "Key": key_upload},
        Metadata={
            "status": "archived",
            "year": "2026",
            "archived_by": "system",
        },
        MetadataDirective="REPLACE",
        ContentType="image/png",
    )
    print(f"Скопирован - {key_copy_replace}")
    show_metadata(s3, BUCKET, key_copy_replace)

    # ---------- 6. Примеры  использования ----------
    print_header("6. Примеры практических metadata")

    examples = {
        "business/invoice-001.pdf": {
            "author": "Ivan",
            "department": "finance",
            "document_type": "invoice",
            "client_id": "12345",
        },
        "pipeline/input/data.csv": {
            "status": "uploaded",
            "uploaded_by": "service-backend",
            "request_id": "req-555",
        },
        "users/42/avatar.png": {
            "user_id": "42",
            "upload_session": "abc-123",
            "app_version": "1.4.2",
        },
    }

    for key, meta in examples.items():
        s3.upload_file(
            Filename=str(LOCAL_FILE),
            Bucket=BUCKET,
            Key=key,
            ExtraArgs={
                "ContentType": "application/octet-stream",
                "Metadata": meta,
            },
        )
        print(f"Загружен: {key}")
        print(f"  metadata: {meta}")

    # ---------- 7. Финальный список объектов ----------
    print_header("7. Все объекты в бакете")

    resp = s3.list_objects_v2(Bucket=BUCKET)
    for obj in resp.get("Contents", []):
        head = s3.head_object(Bucket=BUCKET, Key=obj["Key"])
        print(f"{obj['Key']:40} | {head.get('Metadata', {})}")

    print_header("Готово")
    print(f"Бакет: {BUCKET}")
    print("Можно проверить через AWS CLI:")
    print(f"  aws --endpoint-url {ENDPOINT} s3api head-object --bucket {BUCKET} --key {key_upload}")


if __name__ == "__main__":
    main()