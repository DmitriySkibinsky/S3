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
    # 1 Создание Bucket
    print_header('1. create_bucket()')
    s3.create_bucket(Bucket=bucket_name)
    print('Bucket created')

    # 2 Список Buckets
    print_header('2. list_buckets()')
    response = s3.list_buckets()
    print(f"Всего bucket: {len(response['Buckets'])}")
    for bucket in response['Buckets']:
        print(f'Bucket: {bucket['Name']}, создан: {bucket["CreationDate"]}')

    # 3 Загрузить объекты
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


    # 4 Список объектов
    print_header('4. list_objects_v2()')
    response = s3.list_objects_v2(Bucket=bucket_name)
    print(f'Обьектов в бакете: {response.get('KeyCount', 0)} \n')

    for object in response.get('Contents', 0):
        print(f'  Key: {object['Key']}')
        print(f'  Size: {object["Size"]} байт')
        print(f'  LastModified: {object["LastModified"]}')
        print(f'  ETag: {object["ETag"]}')
        print('=' * 65)

    # 5 Скачать объект
    print_header('5. get_object()')
    response = s3.get_object(Bucket=bucket_name, Key='hello.txt')
    body = response['Body'].read().decode('utf-8')
    print(f'Содержимое {body}')
    print(f'ContentType: {response["ContentType"]}')
    print(f'Metadata: {response["Metadata"]}')

    # 6 Метаданные объекта
    print_header("6. head_object()")
    head = s3.head_object(Bucket=bucket_name, Key="photos/2024/summer.jpg")
    print(f"  Key          : photos/2024/summer.jpg")
    print(f"  Size         : {head['ContentLength']} байт")
    print(f"  ContentType  : {head['ContentType']}")
    print(f"  ETag         : {head['ETag']}")
    print(f"  LastModified : {head['LastModified']}")
    print(f"  Metadata     : {head.get('Metadata', {})}")

    # 7 Скопировать объект
    print_header("7. copy_object()")
    s3.copy_object(
        Bucket=bucket_name,
        CopySource={"Bucket": bucket_name, "Key": "hello.txt"},
        Key="hello-copy.txt",
    )
    print("  hello.txt - hello-copy.txt")

    response = s3.list_objects_v2(Bucket=bucket_name)
    print(f"  Теперь объектов: {response.get('KeyCount', 0)}")

    # 8 Удалить один объект
    print_header("8. delete_object()")
    s3.delete_object(Bucket=bucket_name, Key="docs/notes.md")
    print(" docs/notes.md удалён")

    # 9 Удалить несколько объектов
    print_header("9. delete_objects()")
    response = s3.list_objects_v2(Bucket=bucket_name)
    keys_to_delete = [{"Key": obj["Key"]} for obj in response.get("Contents", [])]

    if keys_to_delete:
        s3.delete_objects(
            Bucket=bucket_name,
            Delete={"Objects": keys_to_delete}
        )
        print(f"  Удалено объектов: {len(keys_to_delete)}")
        for k in keys_to_delete:
            print(f"    - {k['Key']}")

    # 10 Удалить бакет
    print_header("10. delete_bucket()")
    s3.delete_bucket(Bucket=bucket_name)
    print(f"  Бакет '{bucket_name}' удалён")


except:
    pass