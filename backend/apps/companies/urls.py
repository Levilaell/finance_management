from django.urls import path
from rest_framework.response import Response
from rest_framework.views import APIView


class CompaniesView(APIView):
    def get(self, request):
        return Response({"message": "Companies endpoint"})

app_name = 'companies'

urlpatterns = [
    path('', CompaniesView.as_view(), name='companies'),
]