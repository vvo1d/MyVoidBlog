---
title: Урок 4. Формы и обработка данных во Flask
date: 2026-03-25
tags: [Flask, Jinja2]
published: true
---

# Урок 4. Формы и обработка данных во Flask

В этом уроке мы научимся **принимать данные от пользователя** через HTML-формы, обрабатывать их на сервере и делать сайт по-настоящему интерактивным.

---

## 📌 Что такое HTTP-методы и зачем они нужны

Когда браузер общается с сервером, он использует разные **HTTP-методы**:

- **GET** — запрос данных (открыть страницу, получить информацию). Безопасный, можно сохранять в закладки.
- **POST** — отправка данных на сервер (отправить форму, создать пост, зарегистрироваться). Изменяет состояние сервера.

Формы по умолчанию используют метод `GET`, но для отправки данных почти всегда нужно использовать **`POST`**.

---

## 🛠 Подключение обработки форм во Flask

Для работы с данными форм импортируем `request`:

```python
from flask import Flask, render_template, request, redirect, url_for
Базовый пример маршрута с формой
Python@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        # Получаем данные из формы
        name = request.form.get('name')          # безопасно, возвращает None если поля нет
        email = request.form.get('email')
        message = request.form.get('message')

        # Здесь можно сохранить данные в базу, отправить на почту и т.д.
        print(f"Новое сообщение от {name} ({email}): {message}")

        return "Спасибо! Ваше сообщение получено."

    # Если GET — просто показываем форму
    return render_template('feedback.html')
```
> Важно: всегда указывайте methods=['GET', 'POST'], иначе Flask по умолчанию разрешит только GET.

## 📄 Создание HTML-формы
Создаём файл `templates/feedback.html`:

```HTML
{% extends 'base.html' %}

{% block title %}Обратная связь{% endblock %}

{% block content %}
<h1>Напишите нам</h1>

<form method="POST" action="">
    <p>
        <label>Ваше имя:</label><br>
        <input type="text" name="name" required autofocus>
    </p>
    <p>
        <label>Email:</label><br>
        <input type="email" name="email" required>
    </p>
    <p>
        <label>Сообщение:</label><br>
        <textarea name="message" rows="6" cols="50" required></textarea>
    </p>
    <button type="submit">Отправить сообщение</button>
</form>
{% endblock %}
```
Полезные атрибуты форм:

* `required` — обязательное поле
* `autofocus` — автоматически ставит курсор
* `type="email"` — валидация email в браузере
* `action=""` — отправка на текущий URL (можно указать другой)


## 🔄 Добавляем форму создания постов в блог
Обновляем маршрут /blog в app.py:


```Python

# Глобальный список постов (пока храним в памяти)
posts = []

@app.route('/blog', methods=['GET', 'POST'])
def blog():
    if request.method == 'POST':
        title = request.form.get('title')
        text = request.form.get('text')

        if title and text:  # простая валидация
            posts.append({
                "title": title,
                "text": text,
                "date": datetime.now().strftime("%d.%m.%Y в %H:%M")
            })
            return redirect(url_for('blog'))  # переадресация, чтобы не было повторной отправки при обновлении

        else:
            return "Ошибка: заголовок и текст обязательны!"

    return render_template('blog.html', posts=posts)

```
Не забудьте импортировать:
`Pythonfrom datetime import datetime`

📄 Полная версия blog.html

```HTML
{% extends 'base.html' %}

{% block title %}Блог{% endblock %}

{% block content %}
<h1>📝 Мой блог</h1>

<h2>✍️ Добавить новый пост</h2>

<form method="POST">
    <p>
        <label>Заголовок поста:</label><br>
        <input type="text" name="title" required style="width: 500px; padding: 8px;">
    </p>
    <p>
        <label>Текст поста:</label><br>
        <textarea name="text" rows="8" cols="60" required></textarea>
    </p>
    <button type="submit" style="padding: 12px 24px; font-size: 16px;">Опубликовать пост</button>
</form>

<hr>

<h2>📚 Опубликованные посты ({{ posts|length }})</h2>

{% if posts %}
    {% for post in posts %}
        <article style="margin-bottom: 40px; padding: 15px; border-left: 5px solid #007bff;">
            <h3>{{ post.title }}</h3>
            <p>{{ post.text }}</p>
            <small><strong>Опубликовано:</strong> {{ post.date }}</small>
        </article>
    {% endfor %}
{% else %}
    <p>Пока нет постов. Напишите первый!</p>
{% endif %}

{% endblock %}
```

## 🛡️ Важные моменты и лучшие практики

* Никогда не используйте request.form['name'] — если поля нет, будет ошибка 400. Всегда используйте .get().
* Валидация — проверяйте данные на сервере, даже если есть required в HTML.
* Переадресация после POST (Post/Redirect/Get) — используйте redirect() и url_for(), чтобы избежать повторной отправки формы при обновлении страницы.
* Безопасность — в следующих уроках мы подключим CSRF-защиту через Flask-WTF.
* Хранение данных — пока используем список в памяти. При перезапуске сервера данные пропадут (это нормально на данном этапе).


## 🎯 Задание к уроку

* Создать страницу /feedback с формой обратной связи (имя, email, сообщение).
* Добавить форму создания постов на странице /blog.
* Реализовать сохранение постов в список posts.
* Сделать переадресацию после успешной публикации.
* Добавить простую валидацию (проверка, что поля не пустые).
* Дополнительно (рекомендуется): вывести количество постов рядом с заголовком блога.


## 🧠 Что ты освоил в этом уроке

* Разницу между GET и POST запросами
* Как работать с объектом request и формой
* Как принимать и обрабатывать данные от пользователя
* Паттерн Post/Redirect/Get
* Основы валидации данных
* Как делать сайт интерактивным


# 🚀 Что дальше
В следующем уроке:

* Подключение базы данных SQLite
* Создание моделей данных
* Постоянное хранение постов
* Полноценный CRUD (Create, Read, Update, Delete)

Теперь блог уже умеет принимать данные от пользователя — это огромный шаг к настоящему веб-приложению! 🔥