from django.contrib.auth import views as auth_views
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    path('', views.frontpage, name='frontpage'),
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('showusers/', views.render_logged_in_user_list, name='user_push'),
    path('contact/', views.contact, name='contact'),
    path('webpush/', include('webpush.urls')),
    path('send_push', views.send_push),
    path('sw.js', TemplateView.as_view(template_name='sw.js', content_type='application/x-javascript')),
              ]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
