from django.urls import path
from rest_framework.response import Response
from rest_framework.views import APIView


class AuthView(APIView):
    def get(self, request):
        return Response({"message": "Authentication endpoint"})

app_name = 'authentication'

urlpatterns = [
    path('', AuthView.as_view(), name='auth'),
]