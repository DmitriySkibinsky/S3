### Теория

У каждого объекта в S3 есть метаданные — служебная информация о файле.

Их два типа:

---

### 1. System metadata (системные)

Создаются и управляются самим S3. Ты их частично можешь задавать при загрузке, но многие выставляются автоматически.

|Метаданные|Что означает|Кто задаёт|
|---|---|---|
|Content-Type|Тип файла (image/png, text/plain)|Ты / S3|
|Content-Length|Размер в байтах|S3|
|ETag|Хэш содержимого|S3|
|Last-Modified|Дата последнего изменения|S3|
|Content-Encoding|Например gzip|Ты|
|Content-Disposition|Как браузер откроет файл|Ты|
|Cache-Control|Кэширование|Ты|
|x-amz-storage-class|Класс хранения|Ты / S3|
|x-amz-server-side-encryption|Шифрование|Ты / S3|
|x-amz-version-id|ID версии (если versioning)|S3|

---

### 2. User-defined metadata (пользовательские)

Ты задаёшь сам. Всегда имеют префикс x-amz-meta-.

Примеры:

```
x-amz-meta-author = Ivan
x-amz-meta-project = lab
x-amz-meta-department = backend
x-amz-meta-status = archived
```

**Ограничения:**

- Только **ASCII**-символы (кириллица нельзя)
- Общий размер всех user-metadata ≤ **2 КБ**
- Ключи нечувствительны к регистру
- При обычном копировании метаданные **копируются**
- Изменить их можно только через CopyObject (объект сам в себя) с MetadataDirective=REPLACE

---

### Как это выглядит

```
Объект: documents/2026/report.pdf

System metadata:
  Content-Type: image/png
  Content-Length: 132829
  ETag: "6bf55f5bb2db637814f19d78990b5a56"
  Last-Modified: Tue, 04 Aug 2026 ...

User metadata:
  x-amz-meta-author = Ivan
  x-amz-meta-source = lab
```

---

## Команды AWS CLI

### Посмотреть метаданные объекта

Bash

```
aws --endpoint-url http://localhost:9000 s3api head-object \
  --bucket mybucket \
  --key documents/2026/report.pdf
```

В ответе будут и system, и user metadata.

---

### Загрузить файл с user-metadata

Bash

```
aws --endpoint-url http://localhost:9000 s3 cp ./S3_img.png \
  s3://mybucket/documents/report.png \
  --metadata "author=Ivan,project=lab,status=draft" \
  --content-type "image/png"
```

---

### Загрузить + system metadata

Bash

```
aws --endpoint-url http://localhost:9000 s3 cp ./S3_img.png \
  s3://mybucket/documents/report.png \
  --content-type "image/png" \
  --content-disposition "attachment; filename=report.png" \
  --cache-control "max-age=3600" \
  --metadata "author=Ivan,project=lab"
```

---

### Изменить только метаданные (копирование сам в себя)

Bash

```
aws --endpoint-url http://localhost:9000 s3 cp \
  s3://mybucket/documents/report.png \
  s3://mybucket/documents/report.png \
  --metadata "author=Petr,status=updated,reviewed=true" \
  --metadata-directive REPLACE
```

Без --metadata-directive REPLACE старые user-metadata сохранятся, а новые могут не примениться как ожидаешь.

---

### Копирование с сохранением метаданных

Bash

```
aws --endpoint-url http://localhost:9000 s3 cp \
  s3://mybucket/documents/report.png \
  s3://mybucket/archive/report.png
```

По умолчанию user-metadata копируются.

---

### Копирование с заменой метаданных

Bash

```
aws --endpoint-url http://localhost:9000 s3 cp \
  s3://mybucket/documents/report.png \
  s3://mybucket/archive/report.png \
  --metadata "status=archived,year=2026" \
  --metadata-directive REPLACE
```

---

### Через s3api put-object (более низкий уровень)

Bash

```
aws --endpoint-url http://localhost:9000 s3api put-object \
  --bucket mybucket \
  --key documents/report.png \
  --body ./S3_img.png \
  --content-type "image/png" \
  --metadata "author=Ivan,project=lab"
```