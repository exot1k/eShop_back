from rest_framework import serializers

from mainapp.API.serializers import CartProductSerializer
from mainapp.AuthAPI.serializers import UserSerializer
from mainapp.models import Cart, Customer


class CustomerSerializer(serializers.ModelSerializer):
    # user = serializers.SerializerMethodField()
    user = UserSerializer()

    class Meta:
        model = Customer
        fields = ['user', 'email', 'address', 'orders', 'first_name', 'last_name']

    @staticmethod
    def get_user(obj):
        if not (obj.first_name and obj.last_name):
            return obj.id
        return ' '.join([obj.first_name, obj.last_name])


class CartSerializer(serializers.ModelSerializer):
    products = CartProductSerializer(many=True)

    # owner = CustomerSerializer()

    class Meta:
        model = Cart
        fields = '__all__'
