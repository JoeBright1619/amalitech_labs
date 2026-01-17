from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("todo/", views.todos, name="todo"),
    path("todo/create/", views.todo_create, name="todo-create"),
]
