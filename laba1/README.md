# Лабораторные Advanced-трека №1 - Docker

## 1 Подготовка окружения 

```cd ~ ```

```mkdir mycontainer```

```cd mycontainer```

## 2  Скачивание Alpine rootfs

<img width="914" height="462" alt="image" src="https://github.com/user-attachments/assets/06a96600-f7a8-43a0-98b4-35134123f7e0" />


Содержимое Alpine rootfs:


<img width="737" height="486" alt="image" src="https://github.com/user-attachments/assets/7eace9d3-5d87-49e8-8bdc-e4df08d822bc" />

## 3  Создание config.json

<img width="917" height="991" alt="image" src="https://github.com/user-attachments/assets/54a2813c-a283-4116-b928-958951166c99" />

Так раз в секция ```linux.namespaces```

Запрашиваем создание трех типов namespaces:

- pid - изолирует процессы (PID=1 внутри)

- mount - изолирует точки монтирования

- uts - изолирует hostname

Также в секции ```linux.resources``` задаются ограничения ресурсов:

- memory.limit — 128 MB (ограничение памяти)

- cpu.quota/cpu.period — 25% (ограничение CPU)

## 4 Создание Python-утилиты

Создаем файл и добавляем ему право на выполение:

<img width="859" height="107" alt="image" src="https://github.com/user-attachments/assets/87c66cf7-ba1b-48da-a528-2add7256c8e9" />

Утилита mycontainer.py реализует полный жизненный цикл контейнера:

Чтение конфигурации - парсинг config.json

Подготовка окружения - создание директорий и overlayfs

Настройка ограничений - cgroups для ресурсов

Запуск контейнера - изоляция через namespaces

Очистка - размонтирование и удаление cgroups

Основные функции:

**1. ```setup_directories(container_id)```**

<img width="644" height="380" alt="image" src="https://github.com/user-attachments/assets/c1315086-e926-4b89-b654-e8a37e39e7b6" />

Создаем 4 директории:

- upper - слой записи (изменения контейнера)

- work - служебная директория для overlayfs

- merged - точка монтирования объединенной ФС

**2. ```setup_overlayfs(rootfs_path, container_dir)```**

<img width="917" height="492" alt="image" src="https://github.com/user-attachments/assets/03649448-e760-4564-b09c-eaeb19db9b9a" />

где:

- ```lowerdir = rootfs_path``` - базовый слой
- ```upperdir = f"{container_dir}/upper"``` - слой записи
- ```workdir = f"{container_dir}/work"``` - служебный слой
- ```merged = f"{container_dir}/merged"``` - объединенная ФС

**3. ```setup_cgroups(container_id, resources)```**
Настраивает cgroups v2 для ограничения ресурсов:

<img width="1067" height="685" alt="image" src="https://github.com/user-attachments/assets/06f6ca8f-33d7-4542-8966-767ec1771601" />

т.е ├── mycontainer/        - наша группа
    └── {container-id}/    - группа для конкретного контейнера
        ├── memory.max     - 128 MB (ограничение памяти)
        ├── cpu.max        - 25000 100000 (25% CPU)
        └── cgroup.procs   - список PID процессов в группе

**4. ```run_container()```**

<img width="858" height="647" alt="image" src="https://github.com/user-attachments/assets/05091b63-158e-40a6-b988-76cd89224628" />

где:

```unshare_cmd = [ ```

      ```"unshare",
        "--mount",      # изолируем mount namespace
        "--pid",        # изолируем pid namespace  
        "--uts",        # изолируем uts namespace
        "--fork"  ```    # форкаем процесс

**Проверка работоспособности:**

Тест 1:

<img width="1059" height="374" alt="image" src="https://github.com/user-attachments/assets/ddf0b420-a1c5-4ff2-a8e4-703ab6e00f12" />

Видим, что:

- Директории создались в /var/lib/mycontainer/mytest/

- Overlayfs смонтирован

- Внутри контейнера PID=1

- Контейнер завершился с кодом 0 (успешно)

Тест 2 (интерактивный режим):

<img width="1014" height="534" alt="image" src="https://github.com/user-attachments/assets/db27f8dd-64f7-45c7-831c-c9fbd31574bd" />

Так раз видим, что в изоляции процессов у нас только процессы контейнера в количестве двух штук, хотя на самом деле процессов намного больше, тем самым доказываем работоспособность изоляции.

## 5  Запуск тестового контейнера

<img width="1059" height="550" alt="image" src="https://github.com/user-attachments/assets/d34fdc6a-a3ea-43b3-9b0a-c819be833be8" />

Утилита создает уникальную директорию для контейнера с ID test1

Структура директорий:

upper - слой записи (все изменения контейнера)

work - служебная директория для overlayfs

merged - точка монтирования объединенной ФС

Проверка созданных директорий:

<img width="1040" height="207" alt="image" src="https://github.com/user-attachments/assets/3a91fe4b-55b2-452d-b2a9-b493b200ebfb" />

## 6  Проверка overlayfs

Выполняем внутри:

```
echo "test" > /test.txt
ls -la / | grep test.txt
exit
```

<img width="1164" height="588" alt="image" src="https://github.com/user-attachments/assets/76e0ff38-b33c-40dc-8fe3-d222b716e892" />

Видим, что файл создан и виден внутри контейнера, изменения сохранились в верхний слой, оригинальный Alpine не изменился

-> overlays настроен коррекнто

## Общий вывод
В ходе выполнения лабораторной работы была разработана утилита на языке Python, реализующая запуск команд в изолированных контейнерах в соответствии со спецификацией OCI. Утилита демонстрирует основные принципы контейнеризации, лежащие в основе таких технологий, как Docker.
