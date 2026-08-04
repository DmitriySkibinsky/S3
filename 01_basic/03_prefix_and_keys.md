## Теория

S3 — это не файловая система. Внутри бакета нет настоящих папок.
Всё хранится как плоский список объектов, где у каждого объекта есть уникальное имя — Key.


#### Key (ключ)
Это полное имя объекта внутри бакета.

##### Примеры ключей:
```
textphoto.jpg
documents/report.pdf
logs/app/2026-08-03.log
users/42/avatar.png
backup/2026/08/db.sql
```

- Key может содержать / — но это просто символы в имени, а не реальные папки.
- Максимальная длина Key — 1024 байта.
- Key уникален внутри бакета.

#### Prefix (префикс)

Это начало ключа.
Используется для фильтрации и «эмуляции» папок.
Пример:
```
textКлючи в бакете:
  logs/app/2026-08-01.log
  logs/app/2026-08-02.log
  logs/web/2026-08-01.log
  images/photo1.jpg
  images/photo2.jpg
```

Prefix = "logs/"          → 3 объекта
Prefix = "logs/app/"      → 2 объекта
Prefix = "images/"        → 2 объекта
Prefix = "logs/app/2026"  → 2 объекта

Зачем нужны префиксы

- Организация данных (как будто есть папки)
- Фильтрация при листинге
- Lifecycle-правила (удалять/переносить только определённые «папки»)
- Производительность (правильные префиксы помогают масштабироваться)
- Права доступа (можно давать доступ только к logs/*)

### 1. Базовая работа с ключами и префиксами

``` bash
# Список всех объектов
aws --endpoint-url http://localhost:9000 s3 ls s3://mybucket --recursive

# Список только определённого префикса
aws --endpoint-url http://localhost:9000 s3 ls s3://mybucket/logs/ --recursive
aws --endpoint-url http://localhost:9000 s3 ls s3://mybucket/logs/app/ --recursive
```

### 2. Загрузка с нужными ключами и префиксами

```bash
# В корень бакета
aws --endpoint-url http://localhost:9000 s3 cp report.pdf s3://mybucket/

# С префиксом
aws --endpoint-url http://localhost:9000 s3 cp report.pdf s3://mybucket/documents/2026/report.pdf
aws --endpoint-url http://localhost:9000 s3 cp photo.jpg  s3://mybucket/images/2026/08/photo.jpg

# Загрузка целой папки с сохранением структуры
aws --endpoint-url http://localhost:9000 s3 cp ./local-logs/ s3://mybucket/logs/ --recursive
```

### 3. Копирование (CopyObject)

```bash
# Копирование внутри бакета
aws --endpoint-url http://localhost:9000 s3 cp \
  s3://mybucket/documents/report.pdf \
  s3://mybucket/archive/2026/report.pdf

# Копирование + новые метаданные
aws --endpoint-url http://localhost:9000 s3 cp \
  s3://mybucket/documents/report.pdf \
  s3://mybucket/archive/report.pdf \
  --metadata "status=archived,year=2026" \
  --metadata-directive REPLACE

# Копирование целого префикса
aws --endpoint-url http://localhost:9000 s3 cp \
  s3://mybucket/logs/app/ \
  s3://mybucket/backup/logs/app/ \
  --recursive

# Копирование в другой бакет
aws --endpoint-url http://localhost:9000 s3 cp \
  s3://mybucket/photo.jpg \
  s3://otherbucket/images/photo.jpg
```

### 4. Перемещение (move)

```bash
# Переместить один объект
aws --endpoint-url http://localhost:9000 s3 mv \
  s3://mybucket/temp/file.txt \
  s3://mybucket/documents/file.txt

# Переместить весь префикс
aws --endpoint-url http://localhost:9000 s3 mv \
  s3://mybucket/temp/ \
  s3://mybucket/documents/ \
  --recursive
```

### 5. Изменение только метаданных

```bash 
aws --endpoint-url http://localhost:9000 s3 cp \
  s3://mybucket/report.pdf \
  s3://mybucket/report.pdf \
  --metadata "author=Иван,reviewed=true,project=lab" \
  --metadata-directive REPLACE
```

### 6. Удаление по ключу и префиксу

```bash 
# Удалить один объект
aws --endpoint-url http://localhost:9000 s3 rm s3://mybucket/documents/report.pdf
# Удалить весь префикс
aws --endpoint-url http://localhost:9000 s3 rm s3://mybucket/logs/app/ --recursive
```

### 7. Информация об объекте (метаданные + ETag)
```bash
aws --endpoint-url http://localhost:9000 s3api head-object \
  --bucket mybucket \
  --key documents/report.pdf
```

Здесь нужно смотреть поле ETag — если у двух объектов ETag одинаковый, данные с высокой вероятностью общие.

### 8. Поиск объектов
AWS CLI не имеет удобного find, как mc.
Обычно делают так:

```bash
# Все ключи, содержащие "report"
aws --endpoint-url http://localhost:9000 s3api list-objects-v2 \
  --bucket mybucket \
  --query "Contents[?contains(Key, 'report')].[Key, Size, ETag]" \
  --output table
```