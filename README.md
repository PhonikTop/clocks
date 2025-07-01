# Часики — веб-приложение для покер-планирования (Scrum Poker)

## 🚀 Запуск

1. **Настройте переменные окружения**  
    Создайте файл `clocks.env` со следующим содержимым:
    
    ```env
    DEBUG=0
    SECRET_KEY=your-secret-key
    DJANGO_SETTINGS_MODULE=settings.settings
    POSTGRES_USER=your-database-user
    POSTGRES_PASSWORD=your-database-password
    POSTGRES_DB=clocks
    ALLOWED_HOSTS=localhost,watchy-api
    CSRF_TRUSTED_ORIGINS=http://localhost
    DJANGO_SUPERUSER_USERNAME=admin
    DJANGO_SUPERUSER_EMAIL=admin@example.com
    DJANGO_SUPERUSER_PASSWORD=password
    VUE_APP_API_URL=http://localhost:82/api/v1/
    VUE_APP_WS_BASE_URL=ws://localhost:82/ws/
    ```
    
2. **Соберите и запустите проект с помощью Makefile**:
    
    ```bash
    make faststart
    ```

## ⚙️ Функциональные возможности

- 🧩 **Присоединение к комнатам** — пользователи могут подключаться к существующим комнатам или выбирать их из списка.
    
- 👥 **Роли пользователей** — возможность выбрать роль: участник или наблюдатель.
    
- 🕒 **Голосование в реальном времени** — мгновенное отображение хода голосования.
    
- 📊 **Просмотр результатов** — показ результатов голосования, включая среднюю оценку.
    
- 🔄 **Онлайн-состояние в комнате** — отслеживание пользователей, находящихся в комнате.
     
- 🗃 **Кэширование** — хранение данных пользователей и комнат в кэше.
    
- 🛠 **Администрирование** — создание и удаление комнат, просмотр данных о прошлых голосованиях.
