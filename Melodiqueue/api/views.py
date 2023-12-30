from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from urllib.parse import unquote
from allauth.socialaccount.models import SocialAccount


def index(request):
    return render(request, "index.html")

def main(request):
    return render(request, "main.html")

def logout_view(request):
    logout(request)
    return redirect("/")

def generate_response(request, user_input):
    # social_account = SocialAccount.objects.filter(user=request.user, provider='google').first()
    # if social_account:
    #     extra_data = social_account.extra_data
    #     print(extra_data)
    request.session['user_email'] = request.user.email
    result = "You (" + request.session['user_email'] + ") said: " + str(unquote(user_input))
    return JsonResponse({'result': result})
