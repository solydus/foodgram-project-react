from api import views
from django.urls import include, path

urlpatterns = [
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('users/<int:author_id>/subscribe/', views.SubscribeAPIView.as_view()),
]
