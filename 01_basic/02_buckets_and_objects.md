```bash
# 1. Создать бакет
aws s3 mb s3://my-demo-bucket-2024

# или более явно:
aws s3api create-bucket --bucket my-demo-bucket-2024 --region us-east-1

# 2. Список бакетов
aws s3 ls

# 3. Загрузить объект (файл → Object)
echo "Привет, это содержимое объекта!" > hello.txt
aws s3 cp hello.txt s3://my-demo-bucket-2024/hello.txt

# С "папкой" в ключе
aws s3 cp vacation.jpg s3://my-demo-bucket-2024/photos/2024/vacation.jpg

# 4. Список объектов в бакете
aws s3 ls s3://my-demo-bucket-2024 --recursive

# 5. Скачать объект
aws s3 cp s3://my-demo-bucket-2024/hello.txt downloaded.txt

# 6. Посмотреть только метаданные (без скачивания)
aws s3api head-object --bucket my-demo-bucket-2024 --key hello.txt

# 7. Удалить объект
aws s3 rm s3://my-demo-bucket-2024/hello.txt

# 8. Удалить бакет (сначала должен быть пустым)
aws s3 rb s3://my-demo-bucket-2024
# или принудительно со всем содержимым:
aws s3 rb s3://my-demo-bucket-2024 --force

# 9. Просмотр всех метаданных объекта
aws s3api head-object --bucket exp1 --key S3-img.png

/*{                                                                                                                                                                                                                                                                                                                  
    "AcceptRanges": "bytes",
    "LastModified": "2026-08-03T22:10:09+00:00",
    "ContentLength": 132829,
    "ETag": "\"6bf55f5bb2db637814f19d78990b5a56\"",
    "ContentType": "binary/octet-stream",
    "Metadata": {}
}*/
```