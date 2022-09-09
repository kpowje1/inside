# Установка
Предполагается что на стороне сервера, в моём случае рассматривается Ubuntu установлен docker и docker-compose.
Для проверки работоспособности достаточно клонировать только файл docker-compose.yml который дальше сам произведёт магию.
К примеру, если был клонирован весь репозиторий, то сначала переходим в папку inside командой:
```
cd ./inside/
```
Далее необходимо собрать и поднять docker-compose командами:
```
docker-compose build
```
и
```
docker-compose up -d
```
Если после поднятия докера отобразятся строки:
```
Starting inside_postgres_1 ... done
Starting inside_app_1      ... done
```
Значит всё прошло успешно и сервис запущен в докере.

Чтобы проверить запросы и работоспосбность необходимо запустить терминал в контейнере ```inside_app_1```.
Для этого получим id контейнера через команду ```docker ps```, пример ответа:

```
kpowje@kpowje:~/inside$ docker ps
CONTAINER ID   IMAGE             COMMAND                  CREATED          STATUS          PORTS                                       NAMES
b30c71e7fe44   kpowje/inside24   "python main.py runs…"   13 seconds ago   Up 11 seconds   0.0.0.0:5000->5000/tcp, :::5000->5000/tcp   inside_app_1
2f74696d2439   postgres          "docker-entrypoint.s…"   2 hours ago      Up 14 seconds   0.0.0.0:5432->5432/tcp, :::5432->5432/tcp   inside_postgres_1
```

Нас интересует контейнер с ID ```b30c71e7fe44``` по соответствии имени inside_app_1.
Для запуска терминала выполняется команда ```docker exec -it b30c71e7fe44 bash```, где ```b30c71e7fe44``` ID нашего контейнера.

# Проверка работы сервиса
Можно сгенерировать записи в БД через curl:
```
curl -i http://localhost:5000/generate -X GET
```
В ответе отобразятся записи из БД.
Для получения токена необходимо обратиться к эндпоинту ```http://localhost:5000/gettoken```, запрос вида:
```
curl -i http://localhost:5000/gettoken -X POST -d '{"username":"Masha", "password":"pwd2"}' -H "Content-Type: application/json"
```
В ответ мы получим токен, пример:
```
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY2MjcwODMxNCwianRpIjoiNTg3M2NlMDItYjc0ZC00YzVjLTk4MmMtMTkzZWZhY2U1MGNhIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6Ik   1hc2hhIiwibmJmIjoxNjYyNzA4MzE0LCJleHAiOjE2NjI3MDkyMTR9.pEKWVJJVbgPb9IMQNN_bcrgU0eOYG-_SkkgEZdknTP0"
}
```

После получения токена мы можем просмотреть историю осталвенных сообщений или добавить новое, оба варианта адресуются к эндпоинту http://localhost:5000/protected.
Пример с добавлением нового сообщения:
```
curl -i http://localhost:5000/protected -X POST -d '{"name":"Masha", "message":"any message #2"}' -H "Content-Type: application/json" -H "Authorization:Bearer token"
```
где token данные из прошлого запроса (когда получали токен).

Пример с просмотром последних N сообщений:
```
curl -i http://localhost:5000/protected -X POST -d '{"name":"Masha", "message":"history N"}' -H "Content-Type: application/json" -H "Authorization:Bearer token"
```
где token данные из запроса к эндпоинту /gettoken, а N число последних сообщений которые мы хотим получить. История выводится только по пользователю чей токен используется.
То есть нельзя получить через свой токен сообщения чужого пользователя.

