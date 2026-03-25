---
title: Урок 5. База данных SQLite во Flask
date: 2026-03-25
tags: [Flask, SQLite, SQLAlchemy, База данных]
published: true
---

# Урок 5. База данных SQLite во Flask

В предыдущем уроке мы сохраняли посты в обычный список Python.  
При перезапуске сервера все посты исчезали.  
Сегодня мы исправим это и научимся **постоянно хранить данные** с помощью базы данных **SQLite**.

---

## 📌 Зачем нужна база данных?

- Данные сохраняются на жёстком диске и не пропадают при выключении сервера
- Можно работать с большим количеством записей
- Легко искать, сортировать и изменять информацию
- Это стандарт де-факто в веб-разработке

Для начала мы будем использовать **SQLite** — лёгкую, встроенную базу данных, которая не требует отдельного сервера.

---

## 🛠 Установка необходимых библиотек

Выполни в терминале:

```bash
pip install flask-sqlalchemy
Flask-SQLAlchemy — это удобная обёртка над SQLAlchemy, которая отлично интегрируется с Flask.

⚙️ Настройка базы данных в приложении
Обнови начало файла app.py:
Pythonfrom flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
```

## Настройка базы данных

```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# МОДЕЛЬ ДАННЫХ 
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Post "{self.title}">'

```

Что здесь происходит:

* `SQLALCHEMY_DATABASE_URI` — путь к файлу базы данных (blog.db появится автоматически)
* Класс `Post` описывает структуру таблицы в базе
`primary_key=True` — уникальный идентификатор каждой записи
`nullable=False` — поле обязательно для заполнения


## 🗄 Создание базы данных

Добавь этот код один раз в конец файла `app.py` (перед `if __name__ == '__main__':`):
```Python
# Создаём базу данных и таблицы при первом запуске
with app.app_context():
    db.create_all()
```
Теперь при запуске сервера автоматически создастся файл blog.db и таблица post.

## 🔄 Обновляем маршрут блога с использованием базы данных
```Python
@app.route('/blog', methods=['GET', 'POST'])
def blog():
    if request.method == 'POST':
        title = request.form.get('title')
        text = request.form.get('text')

        if title and text:
            new_post = Post(title=title, text=text)
            db.session.add(new_post)
            db.session.commit()               # сохраняем изменения в базе
            return redirect(url_for('blog'))

    # Получаем все посты из базы, отсортированные от новых к старым
    posts = Post.query.order_by(Post.date.desc()).all()
    
    return render_template('blog.html', posts=posts)
```

## 📄 Обновлённый шаблон blog.html
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
        <article style="margin-bottom: 40px; padding: 20px; border-left: 6px solid #007bff; background: #f9f9f9;">
            <h3>{{ post.title }}</h3>
            <p>{{ post.text }}</p>
            <small>
                <strong>Опубликовано:</strong> 
                {{ post.date.strftime('%d.%m.%Y в %H:%M') }}
            </small>
        </article>
    {% endfor %}
{% else %}
    <p>Пока нет ни одного поста. Будь первым!</p>
{% endif %}

{% endblock %}
```

## 🎯 Задание к уроку

1. Установи flask-sqlalchemy
2. Добавь настройку базы данных и модель Post в app.py
3. Создай базу данных с помощью db.create_all()
4. Перепиши маршрут /blog так, чтобы посты сохранялись в SQLite
5. Обнови шаблон blog.html, чтобы он красиво отображал дату
6. Дополнительно (рекомендуется):
* Добавь поле author в модель Post (пока можно задать значение по умолчанию "Admin")
* Сделай так, чтобы новые посты появлялись сверху



## 🧠 Что ты освоил в этом уроке

* Как подключать базу данных к Flask-приложению
* Что такое ORM и зачем нужна модель данных
* Как создавать таблицы с помощью db.create_all()
* Как добавлять записи в базу (db.session.add() + commit())
* Как получать все записи и сортировать их
* Как работать с датами в шаблонах Jinja2


## 🚀 Что дальше
В Уроке 6 мы научимся:

* Просматривать отдельный пост по id
* Редактировать и удалять посты (полноценный CRUD)
* Добавим защиту форм с помощью Flask-WTF и CSRF-токенов
* Сделаем красивые сообщения об успехе и ошибках

Теперь блог хранит данные навсегда — это уже настоящее веб-приложение! 🔥