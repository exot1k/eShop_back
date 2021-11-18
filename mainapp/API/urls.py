from django.urls import path
from rest_framework import routers

from .cart.views import CartViewSet
from .views import ShoesViewSet, CustomerViewSet, ShoesTypeViewSet, ShoesBrandViewSet

ApiRouter = routers.SimpleRouter()
ApiRouter.register('shoes-type', ShoesTypeViewSet, basename='shoes-type')
ApiRouter.register('shoes-brand', ShoesBrandViewSet, basename='shoes-brand')
ApiRouter.register('shoes', ShoesViewSet, basename='shoes')
ApiRouter.register('cart', CartViewSet, basename='cart')

extra_urlpatterns = [
    path('customer/', CustomerViewSet.as_view()),

]
urlpatterns = []
urlpatterns += ApiRouter.urls
urlpatterns.extend(extra_urlpatterns)
