# Интернет-магазин GABRIEL YUSUBOV
**Разработка: студия [Crosswell](https://crosswell.ru)**
##  Описание
Коммерческий проект — интернет-магазин для ИП Юсубов Габриэль Яшарович.

[Демо версия](https://gy.crosswell.ru)

Проект построен по принципам **production-ready**

## Архитектура проекта
- **Backend**: Django
- **Frontend**: Django templates + JS
- **БД**: PostgreSQL
- **Кеш**: Redis
- **Web-server**: Nginx + Gunicorn
- **Контейнеризация**: Docker + docker-compose(локально) + k8s(production)
- **CI/CD**: GitHub Actions (build + deploy на сервер)

## Запуск проекта локально
   ```bash
   docker compose up -d --build
   docker compose exec web python manage.py migrate
   docker compose exec web python manage.py createsuperuser
   ```

## CI/CD
CI/CD реализован на GitHub Actions:

- При пуше в ветку main:
    - собирается Docker-образ
    - пушится в DockerHub
    - деплой на сервер через SSH

## Команда
- **Frontend** - Владимир [scxr1et] Булгаков, Дарья [daryaztsv4] Зайцева
- **Backend** - Игорь [blyaka] Волков
- **DevOps** - Игорь [blyaka] Волков
- **Дизайнер** - Анна Бирюкова
- **Заказчик** - ИП Юсубов Габриэль Яшарович