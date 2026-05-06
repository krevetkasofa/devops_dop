# Лабораторная работа №3 - Облако

## Задание:

``` Реализовать мини-SaaS на основе MinIO: REST API, который по запросу разворачивает изолированное S3-хранилище для пользователя, выдаёт credentials и позволяет управлять жизненным циклом инстанса ```


### Шаг 1: Установка Docker Desktop

Устанавливаем Docker Desktop и проверяем его работу:

```
docker --version

docker ps

docker-compose --version
```

<img width="1056" height="147" alt="image" src="https://github.com/user-attachments/assets/182e590f-0fa9-44c9-863d-cdd6d1964efc" />


### Шаг 2:  Создание структуры проекта

```
mkdir -p ~/minio-saas/docker ~/minio-saas/app

cd ~/minio-saas
```

Итого структруа проекта выглядит так:

```
minio-saas/
├── docker/          # Docker-конфигурация
│   └── docker-compose.yml
└── app/             # Исходный код приложения
    ├── app.py
    ├── Dockerfile
    └── requirements.txt
```


### Шаг 3: Создание docker-compose.yml

Создаем файл ``` ~/minio-saas/docker/docker-compose.yml ```, которое позволит запустить многоконтейнерное приложение одной командой.

В нем описываем:

-  Сервис minio (хранилище)
-  Сервис app (приложение)
-  Сеть minio_network (создаёт виртуальную сеть)
-  Том minio_data (сохраняет данные на диске хоста, при перезапуске он восстанавливаются)

Полный код файла можно найти [тут]((https://github.com/krevetkasofa/devops_dop/tree/main/laba3/Артефакты%20выполнения/docker))

### Шаг 4:  Запуск MinIO

 ```
cd ~/minio-saas/docker

docker compose up -d minio
```

Вывод, который получили:

```
[+] Running 3/3
 ✔ Network docker_minio_network  Created         0.1s
 ✔ Volume "docker_minio_data"    Created         0.0s
 ✔ Container minio-server        Started         0.9s
```

Командой ``` docker compose ps ``` проверяем, по какому адресу доступен MinIO:

<img width="1898" height="152" alt="image" src="https://github.com/user-attachments/assets/31bf56d6-71e9-4ecb-a1d7-1d83d260b264" />


Видим, что консоль MinIO доступна по адресу http://localhost:900


### Шаг 5: Создание виртуального окружения Python

Создаем окружение:

```
cd ~/minio-saas/app

python3 -m venv venv

source venv/bin/activate
```

И устанавливаем зависимости:

```
pip install flask minio

pip freeze > requirements.txt
```
Содержимое файла requirements.txt можно найти тут 

### Шаг 6: Разработка REST API

Создаем файл ``` app.py ```, в котором создаем следующую логику:

- Подключение Flask (веб-фреймворк), MinIO SDK (работа с хранилищем), secrets (генерация ключей), string (алфавит символов)
- Созданием приложение и подключением к MinIO
- Создали пустой словарь ```instances = {}``` для хранения информации о пользователях
- Реализуем функцию  ```generate_credentials()```, которая уникальные ключи доступа для каждого пользователя
- Реализуем эндпоинт ```POST /create-instance```, который принимает JSON с именем пользователя, генерирует ключи, создаёт bucket в MinIO, возвращает креды
- Реализуем эндпоинт  ```DELETE /delete-instance/<bucket_name>```, который сначала удаляет все файлы внутри bucket, потом сам bucket, потом запись из словаря
- Реализуем эндпоинт  ```GET /list-instances```, который запрашивает  у MinIO список всех bucket и добавляет к каждому информацию о владельце из словаря
- Реализуем эндпоинт  ```GET /instance-info/<bucket_name>```, который показывает детальную информацию об одном конкретном хранилище
- Реализуем эндпоинт  ```GET /health```, который проверяет, что приложение может подключиться к MinIO
- Запускаем приложение ```app.run(host='0.0.0.0', port=5000, debug=True)```, где ``` host='0.0.0.0' ``` — принимать запросы извне контейнера; ``` port=5000 — слушать порт 5000 ```; ```debug=True``` — показывать подробные ошибки при разработке

Полный код файла ``` app.py ``` можно найти тут

### Шаг 7:  Создание Dockerfile для приложения

Создаем ``` ~/minio-saas/app/Dockerfile ```, который  описывает, как собрать образ нашего Flask-приложения

```
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
```

### Шаг 8: Запуск всего приложения

```
cd ~/minio-saas/docker
docker compose build --no-cache app
docker compose up -d
```

Вывод:

```
[+] Running 3/3
 ✔ Network docker_minio_network  Created         0.1s
 ✔ Container minio-server        Started         0.6s
 ✔ Container minio-manager       Started         0.7s
```

Проверим работу контейнеров с помощью ```docker compose ps```:

<img width="1657" height="94" alt="image" src="https://github.com/user-attachments/assets/807d7a94-bd91-4342-ba51-e317909cdbc4" />

Видим, что оба контейнера работают


### Шаг 9: Тестирование API

Проверяем,  что каждый эндпоинт правильно обрабатывает запросы и возвращает ожидаемые ответы:

**Тест 1: Health check:**

```
curl http://localhost:5000/health
```

Вывод: 

<img width="1019" height="126" alt="image" src="https://github.com/user-attachments/assets/1c0eee74-d24f-44ea-80e6-9be25aa36801" />

Видим, что  сервис работает и подключён к MinIO, но хранилищ пока нет, тк ещё их не создавали

**Тест 2: Создание хранилища для двух пользователя пользователей:**

Создание хранилища для пользователя vasya:

```
curl -X POST http://localhost:5000/create-instance \
  -H "Content-Type: application/json" \
  -d '{"user_name": "vasya"}'
```

Создание хранилища для пользователя petya:

```
curl -X POST http://localhost:5000/create-instance \
  -H "Content-Type: application/json" \
  -d '{"user_name": "petya"}'
```

<img width="1244" height="641" alt="image" src="https://github.com/user-attachments/assets/4ff77a18-a1a2-41a8-a996-55f3159f499e" />

Видим, что операция выпонена успешно, креды выданы, bucket совпадает с access_key и хранилище готово к использованию

**Тест 3: Список всех хранилищ::**

```
curl http://localhost:5000/list-instances
```

<img width="1116" height="408" alt="image" src="https://github.com/user-attachments/assets/76db9b13-40a7-47c7-9c10-a67d21e322fa" />

Видим два хранилища, которые мы создали в предыдущем этапе

**Тест 4: Удаляение хранилища:**

 Создаем DELETE-запрос — просим удалить хранилище vasya:

```
curl -X DELETE http://localhost:5000/delete-instance/usermu9665mpjrlphiid
```

И проверяем финальный список хранилищ:

```
curl http://localhost:5000/list-instances
```

<img width="1249" height="407" alt="image" src="https://github.com/user-attachments/assets/deb8a8fe-3eee-4883-9079-25cd01c12bf9" />

Видим, что после удаление осталость только одно хранилище petya ->  удаление и изоляция сработали

## Вывод

В ходе лабораторной работы реализован мини-SaaS — облачный сервис на основе MinIO, предоставляющий пользователям изолированные S3-хранилища через REST API.

Конкретно выполнено:

Настроено окружение разработки: WSL 2 + Docker Desktop + Python 3.12

Развёрнут сервер MinIO в Docker-контейнере

Разработан REST API на Flask с пятью эндпоинтами

Реализован полный жизненный цикл хранилища: создание → использование → удаление

Проведено тестирование всех эндпоинтов через curl
