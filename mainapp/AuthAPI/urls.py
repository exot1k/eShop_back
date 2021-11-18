from django.urls import path
from rest_framework import routers

from .views import CheckAuth, LoginView, RegisterView, LogoutView

router = routers.SimpleRouter()

extra_urlpatterns = [
    path('check-auth/', CheckAuth.as_view()),
    path('login/', LoginView.as_view()),
    path('register/', RegisterView.as_view()),
    path('logout/', LogoutView.as_view()),
]

urlpatterns = []
urlpatterns.extend(extra_urlpatterns)
