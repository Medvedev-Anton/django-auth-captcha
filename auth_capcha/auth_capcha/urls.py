from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib.auth import login, get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LogoutView
from django.views.decorators.csrf import csrf_protect

# Главная страница
def index(request):
    return render(request, 'index.html')

# Страница приветствия после входа
def welcome(request):
    return render(request, 'welcome.html')

# Логин (сначала сохраняет user.id в сессию, потом редиректит на капчу)
@csrf_protect
def custom_login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            request.session['pending_user_id'] = user.id  # сохранили ID
            return redirect('/captcha/')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

# Страница капчи
def captcha_view(request):
    return render(request, 'captcha.html')

# Проверка капчи и финальный вход
@csrf_protect
def check_captcha_view(request):
    if request.method == 'POST':
        order = request.POST.get('order', '')
        if order == '1,2,3,4':  # правильный порядок
            user_id = request.session.get('pending_user_id')
            if user_id:
                user = get_user_model().objects.get(id=user_id)
                login(request, user)
                del request.session['pending_user_id']
                if user.is_superuser:
                    return redirect('/admin/')
                else:
                    return redirect('/welcome/')
    # если неправильно — вернуть обратно
    return redirect('/captcha/')

urlpatterns = [
    path('', index, name='home'),
    path('admin/', admin.site.urls),
    path('login/', custom_login_view, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('welcome/', welcome, name='welcome'),
    path('captcha/', captcha_view, name='captcha'),
    path('check-captcha/', check_captcha_view, name='check_captcha'),
]
