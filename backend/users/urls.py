from django.urls import path


from api import views

urlpatterns = [
    path('<int:author_id>/subscribe/', views.SubscribeCreateView.as_view()),
]
