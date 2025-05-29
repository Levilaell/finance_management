"""
Categories app URLs
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'categories'

router = DefaultRouter()
router.register(r'rules', views.CategoryRuleViewSet, basename='category-rule')
router.register(r'suggestions', views.CategorySuggestionViewSet, basename='category-suggestion')
router.register(r'training-data', views.AITrainingDataViewSet, basename='ai-training-data')

urlpatterns = [
    path('', include(router.urls)),
    path('analytics/', views.CategorizationAnalyticsView.as_view(), name='analytics'),
    path('bulk/', views.BulkCategorizationView.as_view(), name='bulk-categorization'),
    path('rule-suggestions/', views.RuleSuggestionsView.as_view(), name='rule-suggestions'),
    path('training/', views.CategoryTrainingView.as_view(), name='category-training'),
]