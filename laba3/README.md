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

Docker Compose позволяет описать и запустить многоконтейнерное приложение одной командой.

Создаем файл ``` ~/minio-saas/docker/docker-compose.yml ```

### Шаг 4:  Запуск MinIO

### Шаг 5: Создание виртуального окружения Python

### Шаг 6: Разработка REST AP

### Шаг 7:  Создание Dockerfile для приложения

### Шаг 8: Запуск всего приложения

### Шаг 9: Тестирование API


## Вывод
