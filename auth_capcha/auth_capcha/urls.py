from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.views import LogoutView

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
