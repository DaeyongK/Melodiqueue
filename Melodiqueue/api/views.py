from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import logout

def index(request):
    return render(request, "index.html")

def main(request):
    return render(request, "main.html")

def logout_view(request):
    logout(request)
    return redirect("/")

def generate_response(request, param):
    result = "You said: " + str(param)
    return JsonResponse({'result': result})
