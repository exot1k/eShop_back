from django.conf import settings
from django.contrib.auth import login, logout
from rest_framework import views, generics, response, permissions, authentication
from rest_framework.response import Response

from .serializers import UserSerializer, LoginSerializer


class CsrfExemptSessionAuthentication(authentication.SessionAuthentication):
    def enforce_csrf(self, request):
        return


class LoginView(views.APIView):
    permission_classes = (permissions.AllowAny,)
    authentication_classes = (CsrfExemptSessionAuthentication,)

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return response.Response(UserSerializer(user).data)


class LogoutView(views.APIView):
    authentication_classes = (CsrfExemptSessionAuthentication,)

    def post(self, request):
        logout(request)
        return response.Response()


class RegisterView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)
    authentication_classes = (CsrfExemptSessionAuthentication,)

    def perform_create(self, serializer):
        user = serializer.save()
        user.backend = settings.AUTHENTICATION_BACKENDS[0]
        login(self.request, user)


class CheckAuth(views.APIView):

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return Response({'is_authenticated': True})
        return Response({'is_authenticated': False})
