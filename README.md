# Lyceum7
Новая _неофициальная_ версия сайта для Лицея №7 города Красноярск (_пока в разработке_).
[Текущий официальный сайт](http://lyceum7.ru/index)

# Иерархия файлов
- alembic – папка с файлами миграций БД.Содержимое генерируется автоматически, поэтому руками лезть
    только в исключительных случаях
- app – папка с приложением, которое считается как python пакет (за счёт наличия 
    [`__init__.py`](https://github.com/Massering/lyceum7/blob/master/app/__init__.py)) 
    при запуске из 
    [`run_server.py`](https://github.com/Massering/lyceum7/blob/master/run_server.py)
- .env – файл с переменными средой окружения для _flask_. 
    Они автоматически загружаются при запуске сервера в 
    [`app/__init__.py`](https://github.com/Massering/lyceum7/blob/master/app/__init__.py)
- alembic.ini – файл относящийся к миграциям и генерируется автоматически, 
    менять его не надо, только в крайних случаях
- config.py – файл с классами конфигов для приложения. Содержит конфиги для 
    разработки, тестирования, продакшена. (Сами конфиги устанавливаются автоматически при
    инициализации, в зависимости от параметров в [`.env`](https://github.com/Massering/lyceum7/blob/master/.env))
- requirements.txt – файл с необходимыми python пакетами
- run_server.py – файл, запускающий сервер

### Установка дополнительных python пакетов
```pip install -r requirements.txt```