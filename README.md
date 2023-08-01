# Дипломный проект Яндекс Практикум продуктовый помощник Foodrgam

Проект представляет собой онлайн-сервис и API для него. На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления выбранных блюд.

## 

[![N|Solid](https://cldup.com/dTxpPi9lDf.thumb.png)](https://nodesource.com/products/nsolid)

[![Build Status](https://travis-ci.org/joemccann/dillinger.svg?branch=master)](https://travis-ci.org/joemccann/dillinger)

## Реализация
- Проект завернут в Docker-контейнеры;
- Образы foodgram_frontend и foodgram_backend запушены на DockerHub;
- Реализован workflow c автодеплоем на удаленный сервер и отправкой сообщения в Telegram;
- Проект к проекту : http://foodgram911.sytes.net/

## Технологии

- Python 3.9
- Django
- Django REST Framework
- PostgreSQL
- Docker
- Gunicorn
- Nginx
- Github Actions


## Запуск проекта на сервере

##### 1. Создать .env файл с переменными окружения в каталоге infra
```
POSTGRES_DB= postgres_db
POSTGRES_USER= postgres_user
POSTGRES_PASSWORD= postgres_password
DB_HOST=db
DB_PORT=5432
```

##### 2. Скопировать содержимое каталога infra на сервер и запустить docker-compose.yml
```
sudo docker compose -f docker-compose.yml up -d
```

##### 2. Применить миграции, собрать статику, и загрузить ингридиенты

```
sudo docker compose exec backend python manage.py migrate
sudo docker compose exec backend python manage.py collectstatic --no-input
sudo docker compose exec backend python manage.py load_ingredients
```
##### 3. Создать суперюзера

```
sudo docker compose exec backend python manage.py createsuperuser
```

## Автор
Кирилл Машталов  https://github.com/kirmasht/

