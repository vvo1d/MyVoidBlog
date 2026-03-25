---
title: Урок 2. Шаблоны во Flask (Jinja2)
date: 2026-03-25
tags: [Flask, Jinja2]
published: true
---

# Урок 2. Шаблоны во Flask (Jinja2)

В прошлом уроке мы создали простой Flask-сервер, который возвращал строки.
Теперь перейдём к полноценной разработке и научимся работать с HTML-шаблонами.

---

## 📌 Почему нельзя писать HTML в Python

На старте можно делать так:

```python
return "<h1>Главная</h1>"
```

Но это плохая практика, потому что:

* ❌ неудобно верстать
* ❌ сложно поддерживать
* ❌ невозможно переиспользовать код
* ❌ нет разделения логики и представления

👉 Поэтому используется **шаблонизатор Jinja2**

---

## 🧠 Что такое Jinja2

**Jinja2** — это шаблонизатор, встроенный во Flask.

Он позволяет:

* писать HTML отдельно от Python
* вставлять данные в HTML
* использовать условия и циклы
* переиспользовать шаблоны

---

## 📁 Структура проекта

Создадим правильную структуру проекта:

```bash
project/
│── app.py
└── templates/
    ├── base.html
    ├── index.html
    ├── about.html
    ├── contact.html
    └── blog.html
```

❗ Важно:

* папка должна называться строго `templates`
* Flask автоматически её использует

---

## ⚙️ Подключение шаблонов во Flask

Обновим `app.py`:

```python
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/blog')
def blog():
    return render_template('blog.html')

if __name__ == '__main__':
    app.run(debug=True)
```

---

## 🧱 Базовый шаблон (base.html)

Это главный файл, который будет использоваться всеми страницами.

```html
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>{% block title %}Мой сайт{% endblock %}</title>

    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 40px;
        }

        nav a {
            margin-right: 10px;
            text-decoration: none;
            color: #333;
        }

        nav a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>

<nav>
    <a href="/">Главная</a>
    <a href="/about">О себе</a>
    <a href="/contact">Контакты</a>
    <a href="/blog">Блог</a>
</nav>

<hr>

{% block content %}
{% endblock %}

</body>
</html>
```

---

# 📄 Главная страница (index.html)

```html
{% extends 'base.html' %}

{% block title %}Главная{% endblock %}

{% block content %}
<h1>Главная страница</h1>
<p>Добро пожаловать на мой сайт 🚀</p>
{% endblock %}
```

---

# 📄 Страница "О себе" (about.html)

```html
{% extends 'base.html' %}

{% block title %}О себе{% endblock %}

{% block content %}
<h1>Обо мне</h1>
<p>Я изучаю Flask и backend-разработку</p>
{% endblock %}
```

---

# 📄 Контакты (contact.html)

```html
{% extends 'base.html' %}

{% block title %}Контакты{% endblock %}

{% block content %}
<h1>Контакты</h1>
<p>Email: example@mail.com</p>
{% endblock %}
```

---

# 📄 Блог (blog.html)

```html
{% extends 'base.html' %}

{% block title %}Блог{% endblock %}

{% block content %}
<h1>Блог</h1>
<p>Здесь скоро появятся мои статьи</p>
{% endblock %}
```

---

## 🔥 Как работает наследование шаблонов

### 1. `base.html`

```html
{% block content %}
{% endblock %}
```

👉 Это "место", куда вставляется контент

---

### 2. Дочерний шаблон

```html
{% extends 'base.html' %}
```

👉 Наследует базовый шаблон

---

### 3. Переопределение блока

```html
{% block content %}
<h1>Контент</h1>
{% endblock %}
```

👉 Вставляет свой HTML

---

## ⚡ Что делает render_template()

```python
return render_template('index.html')
```

👉 Flask:

1. Находит файл в папке `templates`
2. Обрабатывает Jinja2
3. Возвращает готовый HTML в браузер

---

## 🎯 Практическое задание

1. Создать папку `templates`
2. Сделать `base.html`
3. Перенести все страницы в HTML
4. Подключить их через `render_template()`
5. Добавить страницу `/blog`
6. Сделать навигацию

---

## 💡 Дополнительное задание (рекомендуется)

Попробуй:

* добавить CSS стили
* изменить дизайн меню
* добавить footer
* сделать активную ссылку (подсветку текущей страницы)

---

## 🧠 Что ты освоил

После этого урока ты:

* ✅ понял, зачем нужны шаблоны
* ✅ научился работать с Jinja2
* ✅ освоил наследование шаблонов
* ✅ сделал структуру проекта как в реальных приложениях

---

## 🚀 Что дальше

В следующем уроке:

👉 Передача данных в шаблон
👉 Динамические страницы
👉 Переменные и логика в HTML

Это уже настоящий backend 🔥

---

## 📌 Вывод

Шаблоны — это ключевая часть Flask-приложения.
Без них невозможно создать нормальный сайт.

Теперь твой проект стал:

* чище
* масштабируемее
* ближе к реальной разработке
