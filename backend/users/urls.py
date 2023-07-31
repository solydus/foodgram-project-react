from api import views
from django.urls import path

urlpatterns = [
    path('<int:author_id>/subscribe/', views.SubscribeCreateView.as_view()),
]
