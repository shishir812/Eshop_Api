from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [

    path('account/', obtain_auth_token, name='login')
]
