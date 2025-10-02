
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

## 🔐 8. Капча перед входом

После ввода логина и пароля пользователь **не авторизуется сразу**, а:

1. Его ID сохраняется во временной сессии
2. Он переходит на страницу `/captcha/`
3. Там отображается **две сетки 2x2**:

   * Слева — перемешанные части изображения
   * Справа — пустые ячейки
4. Пользователь кликает по картинкам в правильном порядке (`1 → 2 → 3 → 4`)
5. После правильной сборки:

   * происходит авторизация (`login()`)
   * происходит редирект:

     * если `user.is_superuser` → `/admin/`
     * иначе → `/welcome/`

---

### 🗂️ Структура:

#### 🖼 Картинки

```
static/
└── captcha/
    ├── piece1.jpg
    ├── piece2.jpg
    ├── piece3.jpg
    └── piece4.jpg
```

#### 📄 Шаблон `captcha.html`

```html
{% load static %}
<h2>Собери изображение в правильном порядке</h2>
<div id="container">
  <div class="grid" id="source-grid">
    <img src="{% static 'captcha/piece1.jpg' %}" data-id="1">
    <img src="{% static 'captcha/piece2.jpg' %}" data-id="2">
    <img src="{% static 'captcha/piece3.jpg' %}" data-id="3">
    <img src="{% static 'captcha/piece4.jpg' %}" data-id="4">
  </div>
  <div class="grid" id="target-grid">
    <div class="img-slot"></div><div class="img-slot"></div>
    <div class="img-slot"></div><div class="img-slot"></div>
  </div>
</div>
<form method="post" action="/check-captcha/" id="captcha-form">
  {% csrf_token %}
  <input type="hidden" name="order" id="order">
  <button type="submit">Проверить</button>
</form>
<script>
  // JS для перемещения изображений и отправки порядка
</script>
```

---

### 🧠 В `custom_login_view`

Заменили `login(...)` на:

```python
request.session['pending_user_id'] = user.id
return redirect('/captcha/')
```

---

### ✅ Новые вьюхи:

```python
def captcha_view(request):
    return render(request, 'captcha.html')

@csrf_protect
def check_captcha_view(request):
    if request.method == 'POST':
        if request.POST.get('order') == '1,2,3,4':
            user_id = request.session.get('pending_user_id')
            if user_id:
                user = get_user_model().objects.get(id=user_id)
                login(request, user)
                del request.session['pending_user_id']
                return redirect('/admin/' if user.is_superuser else '/welcome/')
    return redirect('/captcha/')
```

---

### 🔗 Новые URL-адреса

```python
path('captcha/', captcha_view, name='captcha'),
path('check-captcha/', check_captcha_view, name='check_captcha'),
```

---

✅ Теперь капча добавлена, и пользователь входит только после её прохождения.

