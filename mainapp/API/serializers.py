from rest_framework import serializers

from mainapp.models import *


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'


class ShoesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shoes
        fields = '__all__'


class ShoesBrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoesBrand
        fields = '__all__'


class ShoesTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoesType
        fields = '__all__'


class ShoesListRetrieveSerializer(serializers.ModelSerializer):
    brand = ShoesBrandSerializer()
    type = ShoesTypeSerializer()

    class Meta:
        model = Shoes
        fields = '__all__'


class CartProductSerializer(serializers.ModelSerializer):
    product = ShoesSerializer()

    class Meta:
        model = CartProduct
        fields = ['id', 'product', 'qty', 'final_price']
