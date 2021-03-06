from django.shortcuts import render
from rest_framework import generics, status, views, permissions
from .serializers import RegisterSerializer, SetNewPasswordSerializer, ResetPasswordEmailRequestSerializer, EmailVerificationSerializer, LoginSerializer, LogoutSerializer
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .utils import Util
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
import jwt
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .renderers import UserRenderer
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .utils import Util
from django.shortcuts import redirect
from django.http import HttpResponsePermanentRedirect
import os

from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth import login,authenticate
from .forms import UserSignUpForm
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes,force_text
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.template.loader import render_to_string
from .token_generator import account_activation_token
# from django.contrib.auth.models import User
from .models import User
from django.core.mail import EmailMessage


def usersignup(request):
  if request.method == 'POST':
    form = UserSignUpForm(request.POST)
    if form.is_valid():
      user = form.save(commit=False)
      user.is_active = False
      user.save()
      current_site = get_current_site(request)
      email_subject = 'Activate Your Account'
      message = render_to_string('activate_account.html',{
        'user':user,
        'domain':current_site.domain,
        'uid':urlsafe_base64_encode(force_bytes(user.pk)), #decode()
        'token':account_activation_token.make_token(user),
      })
      to_email = form.cleaned_data.get('email')
      email = EmailMessage(email_subject,message,to=[to_email])
      email.send()
      return HttpResponse('We have sent you an email,please confirm your email address to complete registration')
  else:
    form = UserSignUpForm()
  return render(request,'signup.html',{'form':form})

def activate_account(request,uidb64,token):
  try:
    uid = force_bytes(urlsafe_base64_decode(uidb64))
    user = User.objects.get(pk=uid)
  except(TypeError,ValueError,OverflowError,User.DoesNotExist):
    user = None
  if user is not None and account_activation_token.check_token(user,token):
    user.is_active = True
    user.save()
    login(request,user)
    return HttpResponse('Your account has been activated successfully')
  else:
    return HttpResponse('Activation link is invalid!')






