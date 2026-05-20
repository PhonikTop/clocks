# Часики — Веб-приложение для покер-планирования (Scrum Poker)
---

## 🚀 Быстрый старт

### 1. Создайте файл `docker-compose.yml`, скопировав содержимое ниже, и обязательно впишите вместо YOUR_DOMAIN_HERE свой домен:


```bash
services:
  watchy-api:
    container_name: watchy-api
    hostname: watchy
    image: ghcr.io/phoniktop/watchy-backend:latest
    env_file:
      - .env
    depends_on:
      - watchy-redis
      - watchy-db
    volumes:
      - backend-static:/app/static
      - ./backend/secret_key:/app/secret_key
    environment:
      - DOMAIN = YOUR_DOMAIN_HERE
	  - DJANGO_SUPERUSER_USERNAME = admin
	  - DJANGO_SUPERUSER_PASSWORD = p@ssw0rd
	  - POSTGRES_USER = postgres
	  - POSTGRES_PASSWORD = postgres
	  - POSTGRES_DB = postgres
    restart: always
    networks:
      - watchy_network

  watchy-redis:
    image: redis:latest
    container_name: watchy-redis
    restart: always
    command: >
      sh -c "exec redis-server /usr/local/etc/redis/redis.conf"
    volumes:
      - ./redis.prod.conf:/usr/local/etc/redis/redis.conf:ro
      - redis-data:/data
    networks:
      - watchy_network

  watchy-db:
    image: postgres:latest
    container_name: watchy-db
    environment:
	  - POSTGRES_USER = postgres
	  - POSTGRES_PASSWORD = postgres
	  - POSTGRES_DB = postgres
    restart: always
    networks:
      - watchy_network

  watchy-frontend:
    image: watchy-frontend
    container_name: ghcr.io/phoniktop/watchy-frontend:latest
    restart: always
    volumes:
      - backend-static:/static
    ports:
      - "82:80"
    networks:
      - watchy_network

networks:
  watchy_network:

volumes:
  redis-data:
  backend-static:
```

### 2. Запустите проект с помощью команды `docker compose up -d`

После успешного запуска приложение будет доступно по вашему домену.

---

## ⚙️ Основные функции

* 🧩 **Подключение к комнатам:** пользователи могут входить в существующие комнаты или выбирать из списка.
* 👥 **Роли:** участник или наблюдатель.
* 🕒 **Голосование в реальном времени** с мгновенным обновлением.
* 📊 **Результаты:** отображение средней оценки и голосов всех участников.
* 🔄 **Онлайн-статус:** отслеживание присутствия пользователей в комнате.
* 🗃 **Кэширование:** хранение данных пользователей и комнат в Redis.
* 🛠 **Администрирование:** создание и управление комнатами, просмотр истории голосований через админ-панель Django.

---

## 🔗 Важные ссылки

* **Админ-панель:**
  https\://your\_domain.com/admin
* **Главная страница с комнатами:**
  https\://your\_domain.com/
* **Прямая ссылка на комнату:**
  https\://your\_domain.com/room/\<ID\_комнаты>/

---

## 🎮 Инструкция по использованию

### Для участников

1. **Вход в комнату:**

   * Откройте главную страницу и выберите комнату.
   * Введите имя и нажмите **Войти**.

2. **Ожидание старта:**

   * Введите описание задачи.
   * Когда все готовы — нажмите **Сохранить**.

3. **Голосование:**

   * Введите свой голос (например, `5`).
   * Ваш статус проголосовавшего отобразится у всех участников.
   * Ждите, пока проголосуют все.

4. **Просмотр результатов:**

   * После окончания голосования отображается средняя оценка и все голоса.
   * Кнопки:

     * **Перезапустить** — начать голосование заново.
     * **Далее** — перейти к следующей задаче.
     * **Завершить** — закончить голосования.

### Для наблюдателей

* При входе выберите **«Войти как наблюдатель»** — вы видите голосование в реальном времени, но голосовать нельзя.

### Для администраторов (через Django admin)

* Стандартный логин:пароль — admin:p@ssw0rd
* Управление комнатами и голосованиями (создание, удаление, редактирование).
* Просмотр истории голосований в комнатах.
