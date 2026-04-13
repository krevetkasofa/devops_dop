# Лабораторная работа №2 - Service Mesh
### Задание: 

```
Необходимо развернуть демонстрационный стенд с использованием выбранного решения Service Mesh и исследовать его базовые возможности:
1. Подключение сервиса к mesh;
2. Межсервисное взаимодействие;
3. Наблюдаемость;
4. Безопасность
По результатам выполнения лабораторной работы необходимо подготовить отчет, в котором должны быть представлены описание стенда, использованные конфигурационные файлы, результаты проверки работы Service Mesh и примеры различных сценариев взаимодействия между сервисами.
```

## Этапы работы:

### 1. Установка Minikube и Kubernetes

<img width="1161" height="541" alt="image" src="https://github.com/user-attachments/assets/fed4c0e8-adfa-4182-a986-a62523c48698" />

kubectl: делаем файл исполняемым и перемещаем в системную папку, чтобы команда kubectl работала отовсюду.

Также установили Minikube и сделали исполняемым. Minikube создаёт локальный кластер Kubernetes на компьютере.


### 2. Установили Linkerd (Service Mesh)

<img width="1025" height="511" alt="image" src="https://github.com/user-attachments/assets/5601867a-f0f5-4f4e-b459-1f79bbc7f7ec" />

Устнавливаем  Linkerd CLI, добавляет папку с Linkerd в переменную окружения PATH.


### 3. Запуск Docker и Minikube

<img width="1052" height="505" alt="image" src="https://github.com/user-attachments/assets/63e0eceb-7c91-451b-b639-fe0dc41840d1" />

Команда ``` minikube config set driver docker ``` говорит Minikube использовать Docker как движок, после нее Minikube будет запускать кластер внутри Docker.

С помощью команды ```minikube start``` запустили Kubernetes-кластер и после проверили, готов ли он к работе:

<img width="644" height="108" alt="image" src="https://github.com/user-attachments/assets/36216b6f-86ab-41d7-b127-45c88cc9d1c4" />


### 4. Установка Linkerd в кластер

Проверяем, можно ли установить  Linkerd в кластер:

<img width="567" height="535" alt="image" src="https://github.com/user-attachments/assets/75f540dd-f62c-450c-bbe6-9553d733badd" />

Убедились, что кластер соответствует требованиям.

Устанавливает Gateway API CRDs: 

``` kubectl apply --server-side -f https://github.com/.../standard-install.yaml ```

<img width="1032" height="386" alt="image" src="https://github.com/user-attachments/assets/cd4a0e4e-3160-4f48-9429-2aad8ed1d737" />

Кластер научился понимать ресурсы Gateway API.

Устанавливаем CRD для Linkerd: 

``` linkerd install --crds | kubectl apply -f -  ``` 

Кластер теперь знает про authorizationpolicies, servers, serviceprofiles и другие ресурсы Linkerd.

И также устанавливаем Control Plane Linkerd:

``` linkerd install --set proxyInit.runAsRoot=true | kubectl apply -f -```

Linkerd Control Plane запущен в неймспейсе linkerd. Control Plane он управляет всеми прокси, хранит политики, выдаёт сертификаты.
 
<img width="1022" height="134" alt="image" src="https://github.com/user-attachments/assets/562e2acf-7076-472a-bf71-f052ded4d21f" />

Устанавливаем в расширение Viz для визуализации: 

``` linkerd viz install | kubectl apply -f -```

И после делаем проверку:

<img width="655" height="661" alt="image" src="https://github.com/user-attachments/assets/d2e9b3e9-ba8d-4e36-a550-456a61ecae22" /> <img width="637" height="423" alt="image" src="https://github.com/user-attachments/assets/b4f96e02-4f28-4f76-849b-8dbb0224ea75" />

Все проверки зелёные - Linkerd полностью установлен и работает.


### 7. Запуск демо-приложения

Создаем изолированное пространство и запускает приложение emojivoto:

<img width="1026" height="438" alt="image" src="https://github.com/user-attachments/assets/1fc2c8ad-7c4d-4ef5-9e4a-e79f2bf1672f" />

В итоге получили 4 микросервиса: emoji, vote-bot, voting, web


К каждому сервису добавили контейнер linkerd-proxy. Теперь все сервисы внутри Service Mesh:

<img width="1016" height="280" alt="image" src="https://github.com/user-attachments/assets/807bbdd2-a001-407b-b0fd-9ca58b2d15a8" />


Проверили, что все  сервисы добавились в Mesh успешно:

<img width="1038" height="308" alt="image" src="https://github.com/user-attachments/assets/02621d2c-a9f4-4b9a-83d8-2a09126f2031" />


### 8. Наблюдаемость и безопасность

Запсукаем веб-интерфейс и также проверяем безопасность = видим, что трафик между этими сервисами зашифрован с помощью mTLS:

<img width="814" height="417" alt="image" src="https://github.com/user-attachments/assets/d7a2f320-2168-4b2d-aac7-23f9038667ab" />



В самом веб-интерфейсе:

**HTTP METRICS:**

<img width="1567" height="683" alt="2026-04-13_17-02-56" src="https://github.com/user-attachments/assets/edf7c93e-42b6-4e8c-a249-0aaf06c3200a" />

Видим таблицу со всеми пространствами имён в кластере и их метриками.

В  ``` emojivoto ``` видим, что все 4 сервиса подключены внутри Service Mesh.

Также видим, что 
- из 100 запросов ~93 успешные, ~7 с ошибками
- Каждую секунду сервисы обрабатывают ~6-7 запросов
- Половина запросов выполняется быстрее 1 миллисекунды
- 95% запросов выполняются быстрее 5 мс
- 99% запросов выполняются быстрее 7 мс

Доказывает, что что Service Mesh собирает метрики в реальном времени без изменения кода приложения.


**TCP METRICS:**

Таблица с сетевыми метриками на транспортном уровне.

<img width="1576" height="607" alt="2026-04-13_17-03-08" src="https://github.com/user-attachments/assets/f92036d7-b0a9-4cd7-93b6-5c74f763e8a4" />

Показывает интенсивность сетевого обмена между сервисами. Даже если приложение не обрабатывает HTTP-запросы, мы видим, что соединения есть и данные передаются.


**EMOJIVOTO:**

Смотрим все все сервисы внутри emojivoto и их метрики:

<img width="1576" height="892" alt="2026-04-13_17-03-39" src="https://github.com/user-attachments/assets/ac0b9e08-67f4-4812-bfc1-c3aa5bc25735" />

Также видим, какие вообще сервисы существуют и как они связаны между собой.


**Поды:**

<img width="1555" height="400" alt="2026-04-13_17-03-49" src="https://github.com/user-attachments/assets/6e55363d-a277-4eca-97f5-0541aad84d5b" />

Те же метрики, но разбитые по отдельным контейнерам:


**TCP МЕТРИКИ ПОДОВ:**

<img width="1559" height="417" alt="2026-04-13_17-04-08" src="https://github.com/user-attachments/assets/2ad963ba-d1a6-4e51-be9c-5d08ff40929a" />

Показывает сетевую активность на низком уровне. Например, web отправляет больше данных (6.8 kB/s), чем получает (188 B/s), потому что он агрегирует ответы от emoji и voting.


### 7. Создали TrafficSplit для canary-релиза

Устанавливаем даптер SMI, который добавляет ресурс TrafficSplit, чтобы кластер научился его понимать:

```
curl -sL https://linkerd.github.io/linkerd-smi/install | sh

export PATH=$PATH:$HOME/.linkerd-smi/bin

linkerd smi install | kubectl apply -f -
```

Теперь Kubernetes понимает, что такое TrafficSplit

Далее создаем canary.yaml : 

Пишем правило разделения трафика, которое может понять  Kubernetes

<img width="647" height="382" alt="image" src="https://github.com/user-attachments/assets/cb914dea-060d-4320-b20e-5b97d2e213bd" />

Говорим Linkerd: "На сервис web-svc направляй 80% трафика на основную версию, 20% — на canary-версию".

Активируем правило и подтвердим, что TrafficSplit существует:

<img width="755" height="116" alt="image" src="https://github.com/user-attachments/assets/e66fd6d6-d79d-4ae8-911e-07d58580bc49" />

### Вывод

В ходе выполнения лабораторной работы был развёрнут стенд на базе Minikube и Linkerd, запущено демо-приложение emojivoto, сервисы подключены к Service Mesh.

**Были исследованы следующие возможности:**

1. **Подключение сервисов к Mesh** — выполнено с помощью `linkerd inject`, подтверждено `MESHED: 1/1`.

2. **Наблюдаемость** — Linkerd автоматически собирает метрики: RPS (0.3–2.5), Latency P95 (1–18 мс), Success Rate (88–100%).

3. **Безопасность** — mTLS шифрует весь трафик между сервисами (колонка `SECURED` в `edges deploy`).

4. **Управление трафиком** — с помощью `TrafficSplit` настроен canary-релиз 80/20.

