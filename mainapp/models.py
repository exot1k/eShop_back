from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone
from django.utils.safestring import mark_safe

from .utils import upload_function


# Create your models here.

class UserManager(BaseUserManager):
    def _create_user(self, phone, password, is_staff, is_superuser, **extra_fields):
        if not phone:
            raise ValueError('Users must have an phone ')

        now = timezone.now()
        user = self.model(

            # email=self.normalize_email(email),
            phone=phone,
            is_staff=is_staff,
            is_active=True,
            is_superuser=is_superuser,
            last_login=now,
            joined_at=now,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def get_by_natural_key(self, username):
        return self.get(**{'{}__iexact'.format(self.model.USERNAME_FIELD): username})

    def create_user(self, phone, password, **extra_fields):
        return self._create_user(phone, password, False, False, **extra_fields)

    def create_superuser(self, phone, password, **extra_fields):
        return self._create_user(phone, password, True, True, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    # email = models.EmailField('Email', max_length=255, unique=True)
    phone = models.CharField(max_length=20, verbose_name='Номер телефона', unique=True, blank=True)
    is_staff = models.BooleanField('Сотрудник?', default=False)
    is_active = models.BooleanField('Активный?', default=True)
    joined_at = models.DateTimeField('Дата регистрации', default=timezone.now)
    objects = UserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


def get_full_name(self):
    return self.first_name + ' ' + self.last_name


def get_short_name(self):
    return self.first_name


class ShoesType(models.Model):
    """Вид обуви"""

    name = models.CharField(max_length=100, verbose_name='Название вида обуви')
    slug = models.SlugField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Вид обуви'
        verbose_name_plural = 'Виды обуви'


class ShoesBrand(models.Model):
    """Бренд"""
    name = models.CharField(max_length=100, verbose_name='Название бренда')
    image = models.ImageField(upload_to=upload_function, null=True, blank=True)
    slug = models.SlugField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Бренд'
        verbose_name_plural = 'Бренды'


class Shoes(models.Model):
    """Обувь"""
    SEX_MALE = 'male'
    SEX_FEMALE = 'female'
    SEX_CHILD = 'child'
    SEX_ALL = 'all'

    SEX_CHOICES = (
        (SEX_MALE, 'Мужские'),
        (SEX_FEMALE, 'Женские'),
        (SEX_CHILD, 'Детские'),
        (SEX_ALL, 'Универсальные'),
    )

    name = models.CharField(max_length=100, verbose_name='Название модели')
    brand = models.ForeignKey(ShoesBrand, verbose_name='Бренд', on_delete=models.CASCADE)
    type = models.ForeignKey(ShoesType, verbose_name='Вид обуви', on_delete=models.CASCADE)
    description = models.TextField(verbose_name='Описание', default='Описание появится позже')
    sex_type = models.CharField(max_length=100, verbose_name='Пол', choices=SEX_CHOICES, default=SEX_ALL)
    stock = models.IntegerField(default=0, verbose_name='Наличие на складе')
    price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Цена')
    offer_of_the_week = models.BooleanField(verbose_name='Предложение недели?', default=False)
    image = models.ImageField(upload_to=upload_function, null=True, blank=True)
    slug = models.SlugField()

    def __str__(self):
        return f"{self.type} {self.sex_type} {self.brand} {self.name}"

    class Meta:
        verbose_name = 'Обувь'
        verbose_name_plural = 'Обувь'


class ImageGallery(models.Model):
    """Галерея изображений"""

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    image = models.ImageField(upload_to=upload_function)
    use_in_slider = models.BooleanField(default=False)

    def __str__(self):
        return f"Изображение для {self.content_object}"

    def image_url(self):
        return mark_safe(f'<img src="{self.image.url}" width="auto" height="200ppx"')

    class Meta:
        verbose_name = 'Галерея изображений'
        verbose_name_plural = 'Галереи изображений'


class CartProduct(models.Model):
    """Продукт для корзины"""
    cart = models.ForeignKey('Cart', verbose_name='Корзина', on_delete=models.CASCADE, related_name='related_products')
    qty = models.PositiveIntegerField(default=1, verbose_name='Количество товара')
    product = models.ForeignKey(Shoes, verbose_name='Товар', on_delete=models.CASCADE)
    final_price = models.DecimalField(max_digits=9, decimal_places=2, null=True, verbose_name='Общая цена')

    def __str__(self):
        return "Продукт: {} (для корзины)".format(self.cart)

    def save(self, *args, **kwargs):
        self.final_price = self.qty * self.product.price
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Продукт корзины'
        verbose_name_plural = 'Продукты корзины'


class Customer(models.Model):
    user = models.OneToOneField(User, null=True, verbose_name='Пользователь', on_delete=models.CASCADE)
    first_name = models.CharField('Имя', null=True, max_length=255, blank=True)
    last_name = models.CharField('Фамилия', null=True, max_length=255, blank=True)
    # phone = models.CharField(max_length=20, verbose_name='Номер телефона', null=True, blank=True)
    email = models.CharField(max_length=20, verbose_name='Почта', null=True, blank=True)
    address = models.CharField(max_length=255, verbose_name='Адрес', null=True, blank=True)
    orders = models.ManyToManyField('Order', verbose_name='Заказы покупателя', related_name='related_order', blank=True)
    is_anonymous_user = models.BooleanField(default=False)
    joined_at = models.DateTimeField('Дата создания покупателя', default=timezone.now)

    def __str__(self):
        if self.is_anonymous_user:
            return str(self.id)
        if not (self.first_name and self.last_name):
            return self.user.phone
        return "Покупатель: {} {}".format(self.first_name, self.last_name)

    class Meta:
        verbose_name = 'Покупатель'
        verbose_name_plural = 'Покупатели'


class Cart(models.Model):
    """Корзина"""
    owner = models.ForeignKey(Customer, null=True, verbose_name='Владелец', on_delete=models.CASCADE)
    products = models.ManyToManyField(CartProduct, null=True, blank=True, related_name='related_cart')
    total_products = models.PositiveIntegerField(default=0)
    final_price = models.DecimalField(max_digits=9, default=0, decimal_places=2, verbose_name='Общая цена')
    in_order = models.BooleanField(default=False)

    def __str__(self):
        return str(f"Корзина {self.id} для пользователя {self.owner} ")

    def save(self, *args, **kwargs):
        if self.id:
            self.total_products = self.products.count()
            self.final_price = sum([cproduct.final_price for cproduct in self.products.all()])
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'


class Order(models.Model):
    STATUS_NEW = 'new'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_READY = 'is_ready'
    STATUS_COMPLETED = 'completed'

    BUYING_TYPE_SELF = 'self'
    BUYING_TYPE_DELIVERY = 'delivery'

    STATUS_CHOICES = (
        (STATUS_NEW, 'Новый заказ'),
        (STATUS_IN_PROGRESS, 'Заказ в обработке'),
        (STATUS_READY, 'Заказ готов'),
        (STATUS_COMPLETED, 'Заказ выполнен')
    )

    BUYING_TYPE_CHOICES = (
        (BUYING_TYPE_SELF, 'Самовывоз'),
        (BUYING_TYPE_DELIVERY, 'Доставка')
    )

    customer = models.ForeignKey(Customer, verbose_name='Покупатель', related_name='related_orders',
                                 on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255, verbose_name='Имя')
    last_name = models.CharField(max_length=255, verbose_name='Фамилия')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    cart = models.ForeignKey(Cart, verbose_name='Корзина', on_delete=models.CASCADE, null=True, blank=True)
    address = models.CharField(max_length=1024, verbose_name='Адрес', null=True, blank=True)
    status = models.CharField(
        max_length=100,
        verbose_name='Статус заказ',
        choices=STATUS_CHOICES,
        default=STATUS_NEW
    )
    buying_type = models.CharField(
        max_length=100,
        verbose_name='Тип заказа',
        choices=BUYING_TYPE_CHOICES,
        default=BUYING_TYPE_SELF
    )
    comment = models.TextField(verbose_name='Комментарий к заказу', null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True, verbose_name='Дата создания заказа')
    order_date = models.DateField(verbose_name='Дата получения заказа', default=timezone.now)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
