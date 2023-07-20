from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api import views

urlpatterns = [
    path('<int:author_id>/subscribe/', views.SubscribeCreateView.as_view()),
]