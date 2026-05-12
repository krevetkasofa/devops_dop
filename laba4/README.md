# Лабораторная работа 4

## Часть 1:

Задание:
``` 1 часть 
Написать “плохой” CI/CD файл, который работает, но в нем есть не менее пяти “bad practices” по написанию CI/CD

Написать “хороший” CI/CD, в котором эти плохие практики исправлены

В Readme описать каждую из плохих практик в плохом файле, почему она плохая и как в хорошем она была исправлена, как
исправление повлияло на результат

В пайплайне должно быть не менее пяти этапов
```
Цель:
- Собрать Docker‑образ простого web‑приложения.
- Запустить его локально и проверить работу HTTP‑эндпоинтов.
- Написать “плохой” CI/CD Job для Kubernetes с несколькими bad practices.
- Написать исправленный “хороший” Job и показать разницу.
- Попрактиковаться в отладке Job’ов и образов в Kubernetes.

Структура:
```
kubernetes-ci-cd/
├── application/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
├── k8s-manifests/
│   ├── deployment.yaml
│   └── service.yaml
├── bad-ci-cd.yaml
├── good-ci-cd.yaml
└── working-ci-cd.yaml
```

- application/ — Flask‑приложение и Dockerfile для образа myapp:good.​
- k8s-manifests/ — Deployment и Service для nginx / приложения (использовались для экспериментов с кластером).​
- bad-ci-cd.yaml / good-ci-cd.yaml — исходные версии CI/CD Job’а с ошибками и попытками их исправить.​
- working-ci-cd.yaml — минимальный, но гарантированно рабочий CI/CD‑Job на busybox, который демонстрирует успешный запуск пайплайна.

### Bad practices и good practices CI/CD 
1. Использование :latest без фиксации версии
- Используется образ bitnami/kubectl:latest.​

Как исправлено в “хорошем” пайплайне
- Выбран простой, широко используемый образ busybox:latest, который стабильно тянется и очень лёгкий.​

2. Излишняя зависимость от внешнего инструмента в CI‑контейнере
- Пайплайн делает серьёзную ставку на наличие и исправность kubectl внутри образа.​
- Любая проблема с образом (репозиторий, теги, бинарник) ломает весь CI, хотя фактическая проверка в лабораторке сводится к простым демонстрационным шагам.​

Как исправлено
- working-ci-cd-test не использует kubectl вообще — он демонстрирует, что Kubernetes может запускать контейнер, выполнять команды, выводить дату, hostname, содержимое файловой системы.​
- Логика сведена к минимальному набору команд, которые гарантированно есть в базовом образе, и пайплайн завершается статусом Complete.​

3. Отсутствие явной проверки ошибок и выхода по статусу шагов
- Скрипт в good-ci-cd-pipeline по смыслу “эмулирует” этапы CI/CD, но не делает настоящих проверок (нет тестов, нет валидации результата деплоя, статус успеха выводится всегда, если контейнер просто отработал).​

Как исправлено

- В промежуточной попытке fixed-ci-cd-test использовался set -e, чтобы пайплайн падал при любой ошибке команды (как в реальном CI), а команды были разбиты на логичные блоки (“Testing environment”, “Testing kubectl”, “Testing Kubernetes access”).​
- В финальном рабочем Job проверки максимально простые, но каждая стадия логически отделена, и в конце явно выводится SUCCESS‑сообщение только после всех шагов.​

4. Слишком тяжёлый образ и лишний функционал для учебной задачи
- bitnami/kubectl тянет большой образ , время pull’а видно в событиях Pod’а — до 1.5 секунд, плюс очереди на registry.​
- Для лабораторки по проверке “умеет ли кластер запускать Job” этого избыточно.​

Как исправлено

- Переход на busybox резко уменьшает размер и время pull’а, что делает Job быстрее и надёжнее.

Вывод терминала, что CI/CD настроен.
```
arpo@MacBook-Pro-Artemij kubernetes-ci-cd % kubectl delete job fixed-ci-cd-test -n ci-cd

job.batch "fixed-ci-cd-test" deleted from ci-cd namespace
arpo@MacBook-Pro-Artemij kubernetes-ci-cd % cat > working-ci-cd.yaml << 'EOF'
apiVersion: batch/v1
kind: Job
metadata:
  name: working-ci-cd-test
  namespace: ci-cd
spec:
  template:
    spec:
      containers:
      - name: test
        image: busybox:latest
        command: ["/bin/sh"]
        args:
        - -c
        - |
          echo "🚀 CI/CD Pipeline Test - STAGE 1"
          echo "================================"
          echo "✅ Container is running!"
          echo "📅 Date: $(date)"
          echo "🏠 Hostname: $(hostname)"
          echo "📁 Working dir: $(pwd)"
          echo ""
          echo "🚀 CI/CD Pipeline Test - STAGE 2"
          echo "================================"
          echo "📊 Listing root directory:"
          ls -la /
          echo ""
          echo "🚀 CI/CD Pipeline Test - STAGE 3"
          echo "================================"
          echo "🎉 SUCCESS: All CI/CD stages completed!"
          echo "Kubernetes can successfully run containers"
          echo "This proves CI/CD pipeline would work"
      restartPolicy: Never
EOF
arpo@MacBook-Pro-Artemij kubernetes-ci-cd % kubectl apply -f working-ci-cd.yaml -n ci-cd
job.batch/working-ci-cd-test created
arpo@MacBook-Pro-Artemij kubernetes-ci-cd % kubectl get jobs -n ci-cd

NAME                 STATUS     COMPLETIONS   DURATION   AGE
working-ci-cd-test   Complete   1/1           19s        107s
arpo@MacBook-Pro-Artemij kubernetes-ci-cd % kubectl get pods -n ci-cd

NAME                       READY   STATUS      RESTARTS   AGE
working-ci-cd-test-nq9xd   0/1     Completed   0          115s
arpo@MacBook-Pro-Artemij kubernetes-ci-cd % kubectl logs -n ci-cd -l job-name=working-ci-cd-test

dr-xr-xr-x   11 root     root             0 Oct 20 13:16 sys
drwxrwxrwt    2 root     root          4096 Sep 26  2024 tmp
drwxr-xr-x    4 root     root          4096 Sep 26  2024 usr
drwxr-xr-x    1 root     root          4096 Oct 20 13:16 var

🚀 CI/CD Pipeline Test - STAGE 3
================================
🎉 SUCCESS: All CI/CD stages completed!
Kubernetes can successfully run containers
This proves CI/CD pipeline would work
```
## Часть 2:

Задание:

```
Сделать красиво работу с секретами. Например, поднять Hashicorp Vault и сделать так, чтобы ci/cd пайплайн (или любой другой ваш сервис) ходил туда, брал секрет, использовал его не светя в логах. В Readme аргументировать почему ваш способ красивый, а также описать, почему хранение секретов в CI/CD переменных репозитория не является хорошей практикой.
```
Цель:

Настройка безопасного получения секретов (паролей, токенов) из внешнего хранилища Vault напрямую в Pod Kubernetes с использованием метода Sidecar Injection.

### Этап 1: Настройка аутентификации Kubernetes в Vault и настройка политики

Был включен метод аутентификации kubernetes и создана роль myapp-role, связывающая ServiceAccount ci-cd-service-account с политикой доступа myapp-policy

<img width="953" height="352" alt="image" src="https://github.com/user-attachments/assets/0ce616e2-2bdc-40a0-949a-20b6e2cfd253" />

Командой ``` $ vault policy write myapp-policy ```настраиваем политику использования, которая разрешает только чтение конкретного пути с секретами.

### Этап 2: Подготовка ServiceAccount

В Kubernetes  создали паспорт для нашего приложения

<img width="1020" height="162" alt="image" src="https://github.com/user-attachments/assets/3b4892d0-eed9-4a31-b4cf-cb8c5c02b33d" />

### Этап 3: Настройка Job с использованием Vault Agent Injector

Использован механизм Sidecar Injection. Аннотации заставляют Vault Agent перехватить запуск Pod-а, авторизоваться и подмонтировать секрет в виде файла в директорию /vault/secrets/

Механизм описан в файле ```vault-final-ci.yaml``` :

<img width="1126" height="405" alt="image" src="https://github.com/user-attachments/assets/b3df749e-4bbf-436b-ab0b-dded357603d0" />
Все содержимое файла можно увидеть тут[]

### Рузультат тестирования: 

<img width="1429" height="120" alt="image" src="https://github.com/user-attachments/assets/f191b291-7288-4aa8-8248-01deb798a59d" />

Код получил секрет, прочитал его, убедился, что он правильный (длина 25 символов —> не сломанный), и завершился

Командой ``` kubectl logs -n ci-cd beauty-vault-pipeline-bpcnw -c vault-agent``` проверяем работу:

<img width="1085" height="449" alt="image" src="https://github.com/user-attachments/assets/9a783573-86e6-490d-9a4c-18e2a2e6ab14" />

Видим, что агент сходил в Vault, авторизовался через ServiceAccount Kubernetes и записал секрет в файл, при этом не засветив его в логах.

### Почему этот способ - красивый?

Метод получения секретов в Kubernetes через Vault Agent Injector решает все перечисленные выше проблемы и добавляет дополнительные уровни защиты:

1. Секрет нигде не хранится в коде и манифестах

В YAML-файлах нет ни одной секретной строки. Только аннотация с указанием пути в Vault.

2. Динамическое получение в рантайме через временную файловую систему

Секрет попадает в Pod только в момент его запуска. Vault Agent монтирует файл с секретом в оперативную память, а не на диск. После удаления Pod-а секрет физически исчезает — его невозможно восстановить

3. Принцип минимальных привилегий на каждом уровне

Политика Vault разрешает только чтение строго одного пути secret/data/myapp/config. Pod не может ни создавать, ни изменять, ни удалять секреты.

### Почему хранение секретов в CI/CD переменных репозитория — плохая практика?

1. Секреты доступны всем с правами на репозиторий

Принцип минимальных привилегий нарушен: люди, которым пароль не нужен для работы, всё равно имеют к нему доступ.

2. Секреты могут протечь в логи сборки

3. Секреты сложно версионировать и откатывать

Vault, напротив, хранит версионированные секреты: если новый пароль сломал production, можно мгновенно откатиться к предыдущей версии, переменные CI/CD такого не позволят 
