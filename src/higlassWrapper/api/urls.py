from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from . import views

urlpatterns = [
	path('', views.Track.as_view(), name='index'),
	path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
]
