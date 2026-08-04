import os
import boto3
from datetime import datetime

s3 = boto3.client(
    "s3",
    endpoint_url="http://localhost:9000",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name="us-east-1",
)

LOCAL_FILE = "./template_data/S3-img.png"
bucket_name = f'demo-lifestyle-{datetime.now().strftime("%Y%m%d-%H%M%S")}'


def print_objects(prefix=""):
    print(f"\n=== Объекты с префиксом '{prefix}' ===")
    resp = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    for obj in resp.get("Contents", []):
        print(f"{obj['Key']:50} | size={obj['Size']:8} | ETag={obj['ETag']}")


def main():
    # 1. Создаём бакет
    try:
        s3.create_bucket(Bucket=bucket_name)
        print(f"Бакет '{bucket_name}' создан")
    except s3.exceptions.BucketAlreadyOwnedByYou:
        print(f"Бакет '{bucket_name}' уже существует")

    # 2. Загрузка файла с разными ключами
    keys = [
        "report.pdf",
        "documents/2026/report.pdf",
        "documents/2026/08/report.pdf",
        "archive/report.pdf",
    ]

    for key in keys:
        s3.upload_file(
            LOCAL_FILE,
            bucket_name,
            key,
            ExtraArgs={
                "Metadata": {
                    "author": "Ivan",
                    "source": "lab",
                }
            },
        )
        print(f"Загружен → s3://{bucket_name}/{key}")

    print_objects()

    # 3. Копирование внутри бакета
    s3.copy_object(
        Bucket=bucket_name,
        Key="backup/2026/report.pdf",
        CopySource={"Bucket": bucket_name, "Key": "documents/2026/report.pdf"},
    )
    print("\nСкопирован: documents/2026/report.pdf → backup/2026/report.pdf")

    # 4. Копирование с заменой метаданных
    s3.copy_object(
        Bucket=bucket_name,
        Key="archive/report-final.pdf",
        CopySource={"Bucket": bucket_name, "Key": "documents/2026/report.pdf"},
        Metadata={
            "status": "archived",
            "year": "2026",
            "reviewed": "true",
        },
        MetadataDirective="REPLACE",
    )
    print("Скопирован с новыми метаданными → archive/report-final.pdf")

    # 5. Изменение метаданных
    s3.copy_object(
        Bucket=bucket_name,
        Key="documents/2026/report.pdf",
        CopySource={"Bucket": bucket_name, "Key": "documents/2026/report.pdf"},
        Metadata={
            "author": "Petr",
            "status": "updated",
        },
        MetadataDirective="REPLACE",
    )
    print("Метаданные обновлены у documents/2026/report.pdf")

    # 6. head-object
    print("\n=== head-object ===")
    for key in [
        "documents/2026/report.pdf",
        "backup/2026/report.pdf",
        "archive/report-final.pdf",
    ]:
        resp = s3.head_object(Bucket=bucket_name, Key=key)
        print(f"{key}")
        print(f"  ETag     : {resp['ETag']}")
        print(f"  Size     : {resp['ContentLength']}")
        print(f"  Metadata : {resp.get('Metadata', {})}")
        print()

    # 7. Список по префиксам
    print_objects("documents/")
    print_objects("archive/")
    print_objects("backup/")

    # 8. Удаление одного объекта
    s3.delete_object(Bucket=bucket_name, Key="report.pdf")
    print("Удалён: report.pdf")

    # 9. Удаление префикса
    def delete_prefix(prefix: str):
        paginator = s3.get_paginator("list_objects_v2")
        deleted = 0
        for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
            objects = page.get("Contents", [])
            if not objects:
                continue
            s3.delete_objects(
                Bucket=bucket_name,
                Delete={"Objects": [{"Key": obj["Key"]} for obj in objects]},
            )
            deleted += len(objects)
        print(f"Удалено {deleted} объектов с префиксом '{prefix}'")

    delete_prefix("logs/")

    print("\nГотово.")


if __name__ == "__main__":
    main()