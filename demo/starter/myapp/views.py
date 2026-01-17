from django.shortcuts import render
from django.http import HttpResponse
from .models import TodoItem

# Create your views here.


def home(request):
    return HttpResponse("you've entered")


def todos(request):
    todo_items = TodoItem.objects.all()
    return render(request, "todo_list.html", {"todo_items": todo_items})


def todo_create(request):
    if request.method == "POST":
        print(request.POST)
        title = request.POST.get("title")
        description = request.POST.get("description")
        completed = request.POST.get("completed")
        print(completed)
        TodoItem.objects.create(title=title, description=description)
    return render(request, "todo_form.html")
