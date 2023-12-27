from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from urllib.parse import unquote


def index(request):
    return render(request, "index.html")

def main(request):
    return render(request, "main.html")

def logout_view(request):
    logout(request)
    return redirect("/")

def generate_response(request, user_input):
    request.session['user_email'] = request.user.email
    result = "You (" + request.session['user_email'] + ") said: " + str(unquote(user_input))
    return JsonResponse({'result': result})
