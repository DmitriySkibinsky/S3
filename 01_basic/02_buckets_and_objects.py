import os
import boto3
from datetime import datetime

def print_header(title: str):
    print("\n" + "=" * 65)
    print(f'  {title}')
    print("=" * 65)


s3 = boto3.client(
    's3',
    endpoint_url='http://localhost:9000',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name='us-east-1'
)

bucket_name = f'demo-lifestyle-{datetime.now().strftime("%Y%m%d-%H%M%S")}'

try:
    # 1
    print_header('1. create_bucket()')
    s3.create_bucket(Bucket=bucket_name)
    print('Bucket created')

    # 2
    print_header('2. list_buckets()')
    response = s3.list_buckets()
    print(f"Всего bucket: {len(response['Buckets'])}")
    for bucket in response['Buckets']:
        print(f'Bucket: {bucket['Name']}, создан: {bucket["CreationDate"]}')

    # 3
    print_header('3. put_objects()')

    objects = [
        {
            "Key": "hello.txt",
            "Body": "Привет из полного lifecycle-скрипта!".encode("utf-8"),
            "ContentType": "text/plain",
            "Metadata": {"author": "Grok", "purpose": "demo"},
        },
        {
            "Key": "photos/2024/summer.jpg",
            "Body": b"fake-jpeg-binary-content-here",
            "ContentType": "image/jpeg",
        },
        {
            "Key": "docs/notes.md",
            "Body": "# Заметки\n\nЭто временный объект.".encode("utf-8"),
            "ContentType": "text/markdown",
        },
        {
            "Key": "data/report.json",
            "Body": '{"status": "ok", "count": 42}'.encode("utf-8"),
            "ContentType": "application/json",
        },
    ]

    for object in objects:
        s3.put_object(Bucket=bucket_name, **object)
        print(object['Key'])

except:
    pass