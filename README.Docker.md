# Docker Deployment Guide

Цей проект підготовлений для деплойменту з використанням Docker та Docker Compose.

## Структура

- `Dockerfile` - образ для Django додатку
- `docker-compose.yml` - оркестрація контейнерів (Django, PostgreSQL, Nginx)
- `docker-entrypoint.sh` - скрипт ініціалізації (міграції, collectstatic, запуск Gunicorn)
- `nginx/` - конфігурація Nginx для обслуговування статичних файлів та проксування запитів

## Передумови

- Docker (>= 20.10)
- Docker Compose (>= 2.0)

## Швидкий старт

1. **Створіть файл `.env`** на основі `.env.example`:
   ```bash
   cp .env.example .env
   ```

2. **Відредагуйте `.env` файл** та встановіть:
   - `SECRET_KEY` - згенеруйте надійний ключ
   - `DB_PASSWORD` - встановіть надійний пароль для бази даних
   - `ALLOWED_HOSTS` - додайте ваш домен
   - `DEBUG=False` - для продакшн

3. **Зберіть та запустіть контейнери**:
   ```bash
   docker-compose build
   docker-compose up -d
   ```

4. **Створіть суперкористувача** (якщо потрібно):
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

5. **Доступ до додатку**:
   - Через Nginx: http://localhost (порт 80)
   - Безпосередньо до Django: http://localhost:8000

## Команди для управління

### Запуск
```bash
docker-compose up -d
```

### Зупинка
```bash
docker-compose down
```

### Перегляд логів
```bash
docker-compose logs -f web
docker-compose logs -f nginx
docker-compose logs -f db
```

### Виконання команд Django
```bash
# Міграції
docker-compose exec web python manage.py migrate

# Створення суперкористувача
docker-compose exec web python manage.py createsuperuser

# Shell
docker-compose exec web python manage.py shell

# Collectstatic
docker-compose exec web python manage.py collectstatic --noinput
```

### Перебудова після змін
```bash
docker-compose build --no-cache
docker-compose up -d
```

## Структура сервісів

### Web (Django)
- Порт: 8000 (внутрішній)
- WSGI сервер: Gunicorn
- Workers: 3
- Timeout: 120 секунд

### Database (PostgreSQL)
- Порт: 5432
- Версія: PostgreSQL 16
- Дані зберігаються в volume `postgres_data`

### Nginx
- Порти: 80 (HTTP), 443 (HTTPS - налаштуйте SSL сертифікати)
- Обслуговує статичні файли та медіа
- Проксує запити до Django

## Продакшн налаштування

### 1. Безпека

В `.env` файлі:
- `DEBUG=False`
- `SECRET_KEY` - використовуйте надійний ключ
- `ALLOWED_HOSTS` - додайте ваш домен
- `SECURE_SSL_REDIRECT=True` - якщо використовуєте HTTPS

### 2. SSL/HTTPS

Для налаштування HTTPS:

1. Отримайте SSL сертифікат (наприклад, через Let's Encrypt)
2. Оновіть `nginx/conf.d/findrive.conf`:
   ```nginx
   server {
       listen 443 ssl http2;
       server_name yourdomain.com;
       
       ssl_certificate /path/to/cert.pem;
       ssl_certificate_key /path/to/key.pem;
       
       # ... решта конфігурації
   }
   
   server {
       listen 80;
       server_name yourdomain.com;
       return 301 https://$server_name$request_uri;
   }
   ```

3. Додайте volumes для сертифікатів в `docker-compose.yml`

### 3. Email налаштування

В `.env` додайте:
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### 4. Backup бази даних

```bash
# Створити backup
docker-compose exec db pg_dump -U findrive_user findrive_db > backup.sql

# Відновити з backup
docker-compose exec -T db psql -U findrive_user findrive_db < backup.sql
```

### 5. Моніторинг

Рекомендується додати:
- Health checks для всіх сервісів
- Логування в централізовану систему
- Моніторинг ресурсів (CPU, пам'ять, диск)

## Troubleshooting

### Проблеми з підключенням до БД
```bash
# Перевірте статус БД
docker-compose exec db pg_isready -U findrive_user

# Перевірте логи
docker-compose logs db
```

### Проблеми зі статичними файлами
```bash
# Перезапустіть collectstatic
docker-compose exec web python manage.py collectstatic --noinput
```

### Проблеми з правами доступу
```bash
# Виправте права для media та static
docker-compose exec web chmod -R 755 /app/media /app/staticfiles
```

## Оновлення

1. Зробіть backup бази даних
2. Зупиніть контейнери: `docker-compose down`
3. Оновіть код
4. Перебудіть образи: `docker-compose build`
5. Запустіть: `docker-compose up -d`
6. Застосуйте міграції: `docker-compose exec web python manage.py migrate`

