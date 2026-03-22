---
title: Как привязать доменное имя к приложению Flask на сервере
date: 2026-03-23
tags: [Flask, Gunicorn, Nginx, Certbot]
published: true
---

# Как привязать доменное имя к приложению Flask на сервере

## Введение

В этом руководстве мы пошагово разберём, как развернуть Flask-приложение на Linux-сервере и привязать к нему собственное доменное имя. В результате ваше приложение будет доступно по адресу вроде `https://example.com` с HTTPS-сертификатом.

**Стек технологий:**

- **Flask** — Python-фреймворк для веб-приложений
- **Gunicorn** — WSGI-сервер для запуска Flask в продакшене
- **Nginx** — обратный прокси-сервер и обработчик статики
- **Certbot** — автоматическое получение SSL-сертификатов от Let's Encrypt
- **systemd** — управление процессом приложения как службой

**Предварительные требования:**

- VPS или выделенный сервер с Ubuntu 22.04+ (или аналогичный дистрибутив)
- Зарегистрированное доменное имя (например, `example.com`)
- SSH-доступ к серверу с правами `sudo`
- Установленный Python 3.8+

---

## Шаг 1. Настройка DNS

Прежде чем сервер сможет обслуживать запросы по вашему домену, нужно настроить DNS-записи у вашего регистратора доменов.

Перейдите в панель управления DNS вашего регистратора и создайте две A-записи:

| Тип  | Имя | Значение            | TTL  |
|------|-----|---------------------|------|
| A    | @   | `IP_ВАШЕГО_СЕРВЕРА` | 3600 |
| A    | www | `IP_ВАШЕГО_СЕРВЕРА` | 3600 |

Замените `IP_ВАШЕГО_СЕРВЕРА` на реальный IP-адрес вашего VPS.

> **Примечание:** Распространение DNS-записей может занять от нескольких минут до 48 часов. Проверить текущее состояние можно командой:

```bash
dig example.com +short
```

---

## Шаг 2. Подготовка сервера

Подключитесь к серверу по SSH и обновите систему:

```bash
ssh user@IP_ВАШЕГО_СЕРВЕРА
sudo apt update && sudo apt upgrade -y
```

Установите необходимые пакеты:

```bash
sudo apt install -y python3 python3-pip python3-venv nginx certbot python3-certbot-nginx
```

---

## Шаг 3. Развёртывание Flask-приложения

### 3.1. Создание директории проекта

```bash
sudo mkdir -p /var/www/myflaskapp
sudo chown $USER:$USER /var/www/myflaskapp
cd /var/www/myflaskapp
```

### 3.2. Настройка виртуального окружения

```bash
python3 -m venv venv
source venv/bin/activate
pip install flask gunicorn
```

### 3.3. Создание приложения

Создайте файл `app.py`:

```python
from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    return "<h1>Привет! Flask работает.</h1>"

if __name__ == "__main__":
    app.run()
```

### 3.4. Создание точки входа для Gunicorn

Создайте файл `wsgi.py`:

```python
from app import app

if __name__ == "__main__":
    app.run()
```

### 3.5. Проверка запуска

```bash
gunicorn --bind 0.0.0.0:8000 wsgi:app
```

Откройте в браузере `http://IP_ВАШЕГО_СЕРВЕРА:8000` — вы должны увидеть приветствие. После проверки остановите Gunicorn комбинацией `Ctrl+C`.

---

## Шаг 4. Создание systemd-службы

Чтобы Gunicorn запускался автоматически и работал в фоне, создайте файл службы:

```bash
sudo nano /etc/systemd/system/myflaskapp.service
```

Вставьте следующее содержимое (замените `user` на ваше имя пользователя):

```ini
[Unit]
Description=Gunicorn для Flask-приложения
After=network.target

[Service]
User=user
Group=www-data
WorkingDirectory=/var/www/myflaskapp
Environment="PATH=/var/www/myflaskapp/venv/bin"
ExecStart=/var/www/myflaskapp/venv/bin/gunicorn --workers 3 --bind unix:myflaskapp.sock --access-logfile /var/log/myflaskapp/access.log --error-logfile /var/log/myflaskapp/error.log wsgi:app

[Install]
WantedBy=multi-user.target
```

Создайте директорию для логов и запустите службу:

```bash
sudo mkdir -p /var/log/myflaskapp
sudo chown user:www-data /var/log/myflaskapp

sudo systemctl daemon-reload
sudo systemctl start myflaskapp
sudo systemctl enable myflaskapp
```

Проверьте статус:

```bash
sudo systemctl status myflaskapp
```

Вы должны увидеть `active (running)`. Также убедитесь, что создался файл сокета:

```bash
ls -la /var/www/myflaskapp/myflaskapp.sock
```

---

## Шаг 5. Настройка Nginx

### 5.1. Создание конфигурации сайта

```bash
sudo nano /etc/nginx/sites-available/myflaskapp
```

Вставьте конфигурацию, заменив `example.com` на ваш домен:

```nginx
server {
    listen 80;
    server_name example.com www.example.com;

    # Максимальный размер загружаемых файлов
    client_max_body_size 10M;

    # Статические файлы (если есть)
    location /static/ {
        alias /var/www/myflaskapp/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Проксирование запросов к Gunicorn
    location / {
        proxy_pass http://unix:/var/www/myflaskapp/myflaskapp.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
    }
}
```

### 5.2. Активация конфигурации

```bash
sudo ln -s /etc/nginx/sites-available/myflaskapp /etc/nginx/sites-enabled/
```

Удалите конфигурацию по умолчанию (если не нужна):

```bash
sudo rm /etc/nginx/sites-enabled/default
```

Проверьте конфигурацию и перезагрузите Nginx:

```bash
sudo nginx -t
sudo systemctl restart nginx
```

На этом этапе ваше приложение уже должно открываться по адресу `http://example.com`.

---

## Шаг 6. Установка SSL-сертификата (HTTPS)

Получите бесплатный сертификат от Let's Encrypt с помощью Certbot:

```bash
sudo certbot --nginx -d example.com -d www.example.com
```

Certbot задаст несколько вопросов:

1. Введите email для уведомлений о продлении.
2. Согласитесь с условиями использования.
3. Выберите автоматическое перенаправление HTTP → HTTPS (рекомендуется).

После завершения Certbot автоматически изменит конфигурацию Nginx, добавив блоки для HTTPS.

Убедитесь, что автоматическое продление работает:

```bash
sudo certbot renew --dry-run
```

Теперь ваш сайт доступен по `https://example.com`.

---

## Шаг 7. Настройка файрвола

Если на сервере включён UFW, откройте необходимые порты:

```bash
sudo ufw allow 'Nginx Full'   # порты 80 и 443
sudo ufw allow OpenSSH         # чтобы не потерять SSH-доступ
sudo ufw enable
sudo ufw status
```

---

## Итоговая архитектура

```
Пользователь
    │
    ▼
[ DNS: example.com → IP сервера ]
    │
    ▼
[ Nginx :443 (HTTPS + SSL) ]
    │
    ▼  (proxy_pass через Unix-сокет)
[ Gunicorn (3 воркера) ]
    │
    ▼
[ Flask-приложение (app.py) ]
```

---

## Полезные команды

| Действие                          | Команда                                      |
|-----------------------------------|----------------------------------------------|
| Перезапуск приложения             | `sudo systemctl restart myflaskapp`          |
| Просмотр логов приложения         | `sudo journalctl -u myflaskapp -f`           |
| Перезапуск Nginx                  | `sudo systemctl restart nginx`               |
| Проверка конфигурации Nginx       | `sudo nginx -t`                              |
| Принудительное продление SSL      | `sudo certbot renew`                         |
| Логи доступа Nginx                | `sudo tail -f /var/log/nginx/access.log`     |
| Логи ошибок Nginx                 | `sudo tail -f /var/log/nginx/error.log`      |

---

## Частые проблемы и решения

### 502 Bad Gateway

Чаще всего это означает, что Gunicorn не запущен или сокет недоступен. Проверьте:

```bash
sudo systemctl status myflaskapp
ls -la /var/www/myflaskapp/myflaskapp.sock
```

Убедитесь, что пользователь Nginx (`www-data`) имеет доступ к файлу сокета.

### Сайт не открывается по домену

- Проверьте DNS: `dig example.com +short` должен возвращать IP вашего сервера.
- Проверьте, что Nginx запущен: `sudo systemctl status nginx`.
- Проверьте файрвол: `sudo ufw status`.

### Ошибка получения SSL-сертификата

- Убедитесь, что домен уже указывает на сервер (DNS распространился).
- Убедитесь, что порт 80 открыт — Certbot использует его для проверки.

---

## Заключение

Вы настроили полноценное продакшен-окружение: Flask-приложение работает через Gunicorn, Nginx выполняет роль обратного прокси и раздаёт статику, а Let's Encrypt обеспечивает HTTPS-шифрование. Домен привязан через A-записи DNS и обслуживается Nginx.

Для дальнейшего улучшения стоит рассмотреть:

- Настройку CI/CD для автоматического деплоя
- Мониторинг через Prometheus + Grafana или аналоги
- Ротацию логов через `logrotate`
- Использование Docker для изоляции окружения
