from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("apply", views.apply_leave, name="apply"),

    path('approve_reject_leave', views.approve_reject_leave, name="approve_reject_leave"),
    path('approved_leaves_list', views.approved_leaves_list, name="approved_leaves_list"),
    path("add_employee", views.add_employee_to_superior, name="add_employee_to_superior"),
    
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
]