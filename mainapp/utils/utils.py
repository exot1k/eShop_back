from rest_framework.pagination import PageNumberPagination

from mainapp.models import Cart, Customer


@staticmethod
def get_or_create_customer(request):
    if request.user.is_authenticated:
        customer, created = Customer.objects.get_or_create(
            user=request.user
        )
        request.session['cart_id'] = customer.id
        return customer

    if request.session.get('cart_id') is None:
        customer = Customer.objects.create(is_anonymous_user=True)
        request.session['cart_id'] = customer.id
        request.session.modified = True
        return customer

    customer, created = Customer.objects.get_or_create(id=request.session['cart_id'])
    return customer


def get_cart_and_products_in_cart(request):
    cart = Cart.objects.filter(owner=get_or_create_customer(request)).first()
    products_in_cart = []
    if cart and cart.products:
        products_in_cart = [cp.product.id for cp in cart.products.all()]
    return cart, products_in_cart


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 9
    page_size_query_param = 'page_size'
