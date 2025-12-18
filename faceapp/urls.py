# faceapp/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('api/register/', views.register_user),
    path('api/login/', views.login_api),
    path('api/logout/', views.logout_api),
    path('api/start/', views.start_attendance),
    path('api/verify-face/', views.verify_face),
    path('api/departments/', views.get_departments),
    path('api/departments/add/', views.add_department),
    # admin helper endpoints for delete etc if you need
    path('api/whoami/', views.whoami),

]
