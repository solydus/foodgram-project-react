[![Foodgram workflow](https://github.com/solydus/foodrammm/actions/workflows/foodgram_workflow.yml/badge.svg)](https://github.com/solydus/foodrammm/actions/workflows/foodgram_workflow.yml)
---

# food_gramm
проект про рецепты, поднят вот тут - http://158.160.25.188/recipes

Как это поднять на своём сервере?

1. клонируем git: git clone ...;
2. делаем файл .env, заполняем его по форме:
  SECRET_KEY=секретный ключ django проекта

  DB_ENGINE=DB_ENGINE
  
  DB_NAME=DB_NAME
  
  POSTGRES_USER=POSTGRES_USER
  
  POSTGRES_PASSWORD=POSTGRES_PASSWORD
  
  DB_HOST=DB_HOST
  
  DB_PORT=DB_PORT
  
4. поднимаем линукс на сервере';
5. Установка Docker:

Обновите пакеты системы командой:
  sudo apt update
  
Установите необходимые пакеты для добавления репозитория Docker:
  sudo apt install apt-transport-https ca-certificates curl software-properties-common
  
Добавьте официальный GPG-ключ Docker:
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
  
Добавьте репозиторий Docker в список источников пакетов:
  echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
  
Установите Docker Engine:
  sudo apt update
  
  sudo apt install docker-ce docker-ce-cli containerd.io
  
Проверьте, что Docker установлен корректно, запустив контейнер hello-world:
  sudo docker run hello-world

  5. Установка Docker Compose:
  6. Загрузите текущую версию Docker Compose:
  sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

Дайте исполняемые права для файла Docker Compose:
  sudo chmod +x /usr/local/bin/docker-compose
  
Проверьте, что Docker Compose установлен корректно, выполнив команду:
  docker-compose --version

8. Копируем файл docker-compose.yml из проекта в папку /home/;
9. Делаем папку /infra/ в директории /home/, в неё копируем файл nginx.conf, прописываем свой ip;
10. Запустите docker compose:
  docker compose up -d --build
11. Сделайте миграции:
  docker compose exec backend python manage.py makemigrations
12. приммените миграции:
  docker compose exec backend python manage.py migrate
13. Перейдите по ip-адресу своего сервера

???

15. profit;
