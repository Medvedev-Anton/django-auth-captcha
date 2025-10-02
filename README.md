
---


Проект на Django + PostgreSQL с реализацией базовой авторизации, разделением по ролям (админ / пользователь), кастомными редиректами и безопасным выходом.

---

## 🚀 1. Установка и запуск проекта

```bash
python -m venv venv
venv\Scripts\activate
pip install django psycopg2
django-admin startproject auth_capcha .
````

---

## 🛠️ 2. Настройка PostgreSQL

В `settings.py`:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "company",
        "USER": "postgres",
        "PASSWORD": "root",
        "HOST": "localhost",
        "PORT": "5432",
    }
}
```

---

## 🧱 3. Миграции и суперпользователь

```bash
python manage.py migrate
python manage.py createsuperuser
```

---

## 📁 4. Шаблоны

Создай структуру:

```
templates/
├── registration/
│   └── login.html
├── index.html
└── welcome.html
```

### `registration/login.html`

```html
<h2>Вход</h2>
<form method="post">
  {% csrf_token %}
  {{ form.as_p }}
  <button type="submit">Войти</button>
</form>
```

---

### `index.html`

```html
<h2>Главная</h2>
<a href="{% url 'login' %}">Войти</a>
```

---

### `welcome.html`

```html
<h1>Привет, {{ user.username }}! Ты авторизовался!</h1>
<form method="post" action="{% url 'logout' %}">
  {% csrf_token %}
  <button type="submit">Выйти</button>
</form>
```

---

## 🧠 5. `urls.py` с кастомной логикой ролей

```python
from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import LogoutView
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect

def index(request):
    return render(request, 'index.html')

def welcome(request):
    return render(request, 'welcome.html')

@csrf_protect
def custom_login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.is_superuser:
                return redirect('/admin/')
            else:
                return redirect('/welcome/')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

urlpatterns = [
    path('', index, name='home'),
    path('admin/', admin.site.urls),
    path('login/', custom_login_view, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('welcome/', welcome, name='welcome'),
]
```

---

## ⚙️ 6. `settings.py`: шаблоны и logout-редирект

```python
TEMPLATES = [
    {
        ...
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        ...
    },
]

LOGOUT_REDIRECT_URL = '/login/'
```

---

## 🧪 7. Запуск

```bash
python manage.py runserver
```

* Перейди на `/`
* Зайди через `/login/`

  * Суперпользователь → редирект в `/admin/`
  * Обычный пользователь → редирект в `/welcome/`
* Нажми “Выйти” → попадёшь на `/login/`

---

## 🔐 8. [Следующий шаг] — добавление капчи

* Пользователь не авторизуется сразу после ввода логина и пароля
* После успешной аутентификации переходит на `/captcha/`
* Проходит визуальную капчу (2x2)
* Только после этого происходит вход и редирект по роли

➡️ *Капча будет реализована на основе изображений и JS, с логикой сборки правильного порядка.*

---
