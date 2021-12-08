from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .serializers import CartSerializer
from ...AuthAPI.views import CsrfExemptSessionAuthentication
from ...models import Cart, CartProduct, Shoes
from ...utils.utils import get_or_create_customer, get_max_age


class CartViewSet(ModelViewSet):
    serializer_class = CartSerializer
    queryset = Cart.objects.all()
    authentication_classes = (CsrfExemptSessionAuthentication,)

    @staticmethod
    def get_or_create_cart(customer):
        cart, created = Cart.objects.get_or_create(owner=customer)
        return cart

    @staticmethod
    def _get_or_create_cart_product(cart: Cart, product: Shoes):
        cart_product, created = CartProduct.objects.get_or_create(
            product=product,
            cart=cart
        )
        return cart_product, created

    @action(methods=["get"], detail=False)
    def current_customer_cart(self, *args, **kwargs):
        response = Response()
        customer = get_or_create_customer(self.request)
        response.set_cookie('customer_id', customer.id, get_max_age(self.request))
        cart = self.get_or_create_cart(customer)
        cart_serializer = CartSerializer(cart)
        response.data = cart_serializer.data
        return response

    @action(methods=['put'], detail=False, url_path='current_customer_cart/add_to_cart')
    def product_add_to_cart(self, *args, **kwargs):
        response = Response()
        product_id = self.request.data['productId']
        customer = get_or_create_customer(self.request)
        response.set_cookie('customer_id', customer.id, get_max_age(self.request))
        cart = self.get_or_create_cart(customer)
        product = get_object_or_404(Shoes, id=product_id)
        cart_product, created = self._get_or_create_cart_product(cart, product)

        if created:
            cart.products.add(cart_product)
            cart.save()
            response.data = {'productId': product.id, "detail": "Товар добавлен в корзину", "added": True}
            return response
        response.data = {'productId': product.id, 'detail': "Товар уже в корзине", "added": False}
        response.status_code = status.HTTP_400_BAD_REQUEST
        return response

    @action(methods=["patch"], detail=False,
            url_path='current_customer_cart/change_qty')
    def product_change_qty(self, *args, **kwargs):
        product_id = self.request.data['productId']
        cart_product = get_object_or_404(CartProduct, product=product_id,
                                         cart=get_object_or_404(Cart, owner=self.request.COOKIES.get('customer_id')))
        cart_product.qty = int(self.request.data['qty'])
        if cart_product.qty == 0:
            cart_product.cart.products.remove(cart_product)
            cart_product.delete()
            cart_product.cart.save()
            return Response({'productId': product_id, 'qty': cart_product.qty, 'inCart': False},
                            status=status.HTTP_200_OK)
        cart_product.save()
        cart_product.cart.save()
        return Response({'productId': product_id, 'qty': cart_product.qty, 'inCart': True},
                        status=status.HTTP_200_OK)

        # @action(methods=["delete"], detail=False, url_path='current_customer_cart/remove_from_cart')
        # def product_remove_from_cart(self, *args, **kwargs):
        #     cart_product_id = self.request.data['productId']
        #     customer = get_or_create_customer(self.request)
        #     cart = self.get_or_create_cart(customer)
        #     cart_product = get_object_or_404(CartProduct, product=cart_product_id)
        #     cart.products.remove(cart_product)
        #     cart_product.delete()
        #     cart.save()
        #     return Response(status=status.HTTP_204_NO_CONTENT)
