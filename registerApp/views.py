from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404, render
from django.http.response import JsonResponse, HttpResponse

from webpush import send_user_notification
import json
from .forms import SignUpForm
from .getUsers import get_all_logged_in_users
from django import template
from .telSend import chat_request
from django.conf import settings

def frontpage(request):
    webpush_settings = getattr(settings, 'WEBPUSH_SETTINGS', {})
    vapid_key = webpush_settings.get('VAPID_PUBLIC_KEY')
    user = request.user
    return render(request, 'frontpage.html', {user: user, 'vapid_key': vapid_key})

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)

        if form.is_valid():
            user = form.save()

            login(request, user)

            return redirect('frontpage')
    else:
        form = SignUpForm()
    
    return render(request, 'signup.html', {'form': form})

def contact(request):
    user = str(request.user)
    chat_request(user)
    return redirect(request.META.get('HTTP_REFERER')) # redirect to previous page

# get push 

register = template.Library()
@register.inclusion_tag('templates/logged_in_user_list.html')
@login_required
@require_GET
def render_logged_in_user_list(request):
    print(list(get_all_logged_in_users()), len(list(get_all_logged_in_users())))
    webpush_settings = getattr(settings, 'WEBPUSH_SETTINGS', {})
    vapid_key = webpush_settings.get('VAPID_PUBLIC_KEY')
    user = request.user
    return render(request, 'logged_in_user_list.html', { 'users': get_all_logged_in_users(), user: user, 'vapid_key': vapid_key })

@require_POST
@csrf_exempt
def send_push(request):
    try:
        body = request.body
        data = json.loads(body)
        print(data)
        print(request.user.id)

        if 'head' not in data or 'body' not in data or 'id' not in data:
            return JsonResponse(status=400, data={"message": "Invalid data format"})

        user_id = data['id']
        user = get_object_or_404(User, pk=user_id)
        payload = {'head': data['head'], 'body': data['body']}
        send_user_notification(user=user, payload=payload, ttl=1000)

        return JsonResponse(status=200, data={"message": "Web push successful"})
    except TypeError:
        return JsonResponse(status=500, data={"message": "An error occurred"})
