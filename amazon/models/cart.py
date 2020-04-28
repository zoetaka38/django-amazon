from django.db import models
from django.db.models import F, Sum
from django.contrib.auth import get_user_model
from ..models import Product

User = get_user_model()


class ShoppingCart(models.Model):

    user = models.OneToOneField(
        User,
        verbose_name = 'ユーザ',
        related_name = 'cart',
        on_delete = models.CASCADE
    )
    @property
    def item_count(self):
        return self.cart_items.all().aggregate(amount = Sum('amount'))['amount']
    @property
    def total_price(self):
        return self.cart_items.all().aggregate(total=Sum(F('product__price') * F('amount')))['total']


class ShoppingCartItem(models.Model):
    cart = models.ForeignKey(
        ShoppingCart,
        related_name = 'cart_items',
        verbose_name = 'ショッピングカート',
        on_delete = models.CASCADE
    )
    product = models.ForeignKey(
        Product,
        verbose_name = '商品',
        on_delete = models.CASCADE
    )
    amount = models.IntegerField(
        verbose_name = '数量'
    )