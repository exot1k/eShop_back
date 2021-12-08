from rest_framework.pagination import PageNumberPagination

from mainapp.models import Cart, Customer


@staticmethod
def get_or_create_customer(request):
    # if cache.get('customer_id') is None:
    if request.COOKIES.get('customer_id') is None:
        customer = Customer.objects.create(is_anonymous_user=True)
        # cache.set('customer_id', customer.id, None)

        return customer

    # customer = Customer.objects.get(id=cache.get('customer_id'))
    customer, create = Customer.objects.get_or_create(id=request.COOKIES.get('customer_id'))

    if request.user.is_authenticated:
        customer.user = request.user
        customer.is_anonymous_user = False
        customer.save()
    return customer


@staticmethod
def get_max_age(request):
    max_age = request.session.get_expiry_age()
    print(max_age)
    return max_age


# if request.user.is_authenticated:
#     customer, created = Customer.objects.get_or_create(
#         user=request.user
#     )
#     # request.session['cart_id'] = customer.id
#     cache.set('customer_id', customer.id, None)
#     return customer
#
# if cache.get('customer_id') is None:
#     customer = Customer.objects.create(is_anonymous_user=True)
#     cache.set('customer_id', customer.id, None)
#     # request.session['cart_id'] = customer.id
#     # request.session.modified = True
#     return customer
#
# customer, created = Customer.objects.get_or_create(id=cache.get('customer_id'))
# return customer


def get_cart_and_products_in_cart(request, customer):
    cart = Cart.objects.filter(owner=customer).first()
    products_in_cart = []
    if cart and cart.products:
        products_in_cart = [cp.product.id for cp in cart.products.all()]
    return cart, products_in_cart


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 9
    page_size_query_param = 'page_size'
