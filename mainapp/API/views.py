from django.core.cache import cache
from rest_framework import viewsets, views
from rest_framework.response import Response

from .serializers import *
from ..AuthAPI.views import CsrfExemptSessionAuthentication
from ..utils.utils import get_cart_and_products_in_cart, StandardResultsSetPagination, get_or_create_customer, \
    get_max_age


class CustomerViewSet(views.APIView):
    authentication_classes = (CsrfExemptSessionAuthentication,)

    def get(self, request, *args, **kwargs):
        # if request.user.is_authenticated:
        #     return Response(CustomerSerializer(Customer.objects.get(user=request.user)).data)
        return Response(CustomerSerializer(Customer.objects.get(id=request.COOKIES.get('customer_id'))).data)

    def patch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            customer = Customer.objects.get(user=request.user)
            serializer = CustomerSerializer(customer, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
            return Response(serializer.data)
        customer = Customer.objects.get(id=cache.get('cart_id'))
        serializer = CustomerSerializer(customer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data)


class ShoesTypeViewSet(viewsets.ModelViewSet):
    queryset = ShoesType.objects.all()
    serializer_class = ShoesTypeSerializer


class ShoesBrandViewSet(viewsets.ModelViewSet):
    queryset = ShoesBrand.objects.all()
    serializer_class = ShoesBrandSerializer


class ShoesViewSet(viewsets.ModelViewSet):
    serializer_class = ShoesListRetrieveSerializer
    pagination_class = StandardResultsSetPagination
    lookup_field = 'slug'

    @staticmethod
    def check_cart_and_set_qty(serializer_data, products_in_cart, cart):
        for product in serializer_data:
            product['in_cart'] = False
            if product['id'] in products_in_cart:
                product['in_cart'] = True
                product['qty'] = cart.products.filter(product=product['id']).first().qty
        return serializer_data

    def get_queryset(self):
        queryset = Shoes.objects.all()
        filters = {}
        sex_type = self.request.query_params.get('sexType')
        shoes_brand = self.request.query_params.get('shoesBrand')
        shoes_type = self.request.query_params.get('shoesType')
        if sex_type is not None:
            filters['sex_type'] = sex_type

        if shoes_brand is not None:
            filters['brand'] = ShoesBrand.objects.filter(slug=shoes_brand).first().id

        if shoes_type is not None:
            filters['type'] = ShoesType.objects.filter(slug=shoes_type).first().id

        queryset = queryset.filter(**filters)

        return queryset

    def list(self, request, *args, **kwargs):
        cart = products_in_cart = []
        response = Response()
        queryset = self.filter_queryset(self.get_queryset())
        if self.request.COOKIES.get('customer_id') is not None:
            customer = get_or_create_customer(self.request)
            cart, products_in_cart = get_cart_and_products_in_cart(request, customer.id)
            response.set_cookie('customer_id', customer.id, get_max_age(self.request))
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(queryset, many=True)
        serializer_data = serializer.data
        if page is not None:
            serializer = ShoesListRetrieveSerializer(page, many=True)
            serializer_data = serializer.data
            serializer_data = self.check_cart_and_set_qty(serializer_data, products_in_cart, cart)
            # for product in serializer.data:
            #     product['in_cart'] = True if product['id'] in products_in_cart else False
            return self.get_paginated_response(serializer_data)
        if cart is not None:
            # for product in serializer_data:
            #     product['in_cart'] = False
            #     if product['id'] in products_in_cart:
            #         product['in_cart'] = True
            #         product['qty'] = cart.products.filter(product=product['id'], cart=cart.id).first().qty
            serializer_data = self.check_cart_and_set_qty(serializer_data, products_in_cart, cart)
        response.data = serializer_data
        return response
