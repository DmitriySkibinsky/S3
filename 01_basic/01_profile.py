import os
import boto3

s3 = boto3.client(
    's3',
    endpoint_url='http://localhost:9000',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name='us-east-1'
)

# после подключения становятся доступными все операции с S3

response_to_clear = s3.list_buckets()
for bucket in response_to_clear['Buckets']:

    bucket_name = bucket['Name']
    objects = s3.list_objects_v2(Bucket=bucket_name)

    if 'Contents' in objects:
        for content in objects['Contents']:
            s3.delete_object(
                Bucket=bucket_name,
                Key=content['Key']
            )

    s3.delete_bucket(Bucket=bucket_name)


print(f"Пусто: {s3.list_buckets()['Buckets']}")

# создадим bucket
s3.create_bucket(Bucket='exp1')
s3.create_bucket(Bucket='exp2')
s3.create_bucket(Bucket='exp3')

# просмотреть какие есть корзины
response = s3.list_buckets()

for bucket in response['Buckets']:
    print(bucket['Name'])

# удалить bucket
s3.delete_bucket(Bucket='exp3')

# загрузить объект
s3.upload_file('./template_data/S3-img.png', 'exp1', 'S3-img.png')

# просмотреть содержимое

response = s3.list_objects_v2(Bucket='exp1')

for obj in response.get('Contents', []):
    print(obj['Key'], obj['Size'])