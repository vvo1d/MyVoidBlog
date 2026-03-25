---
title: Урок 3. Передача данных в шаблоны Flask (Jinja2)
date: 2026-03-25
tags: [Flask, Jinja2]
published: true
---


# Урок 3. Передача данных в шаблоны Flask (Jinja2)

В этом уроке я научился делать динамические страницы и передавать данные из Python в HTML.

---

## 📌 Передача переменных

Во Flask данные передаются через `render_template()`:

```python
return render_template('index.html', name='Victor')
```

---

## 📄 Использование в HTML

```html
<h1>Привет, {{ name }}</h1>
```

---

## 🔁 Передача списков

```python
posts = ["Пост 1", "Пост 2"]
return render_template('blog.html', posts=posts)
```

---

## 🔄 Циклы

```html
{% for post in posts %}
    <p>{{ post }}</p>
{% endfor %}
```

---

## 🔀 Условия

```html
{% if posts %}
    <p>Есть посты</p>
{% else %}
    <p>Постов нет</p>
{% endif %}
```

---

## 🛠 Пример блога

```python
@app.route('/blog')
def blog():
    posts = [
        {"title": "Первый пост", "text": "Мой первый блог"},
        {"title": "Второй пост", "text": "Изучаю Flask"}
    ]
    return render_template('blog.html', posts=posts)
```

---

```html
{% for post in posts %}
    <h2>{{ post.title }}</h2>
    <p>{{ post.text }}</p>
{% endfor %}
```

---

## 🎯 Задание

* Передать имя на главную страницу
* Сделать список постов
* Добавить условие (авторизация)

---

## 🧠 Вывод

В этом уроке я:

* научился передавать данные в шаблоны
* использовал циклы и условия
* сделал динамический сайт
