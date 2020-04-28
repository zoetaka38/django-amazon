from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse, HttpResponseBadRequest
from ..models import Product, ShoppingCart, ShoppingCartItem
from django.urls import reverse


class ShoppingCartDetail(LoginRequiredMixin, generic.DetailView):
    model = ShoppingCart
    template_name = "amazon/shopping_cart.html"

    def post(self, request, *args, **kwargs):
        user = request.user
        product_pk = request.POST.get('product_pk')
        product = Product.objects.get(pk = product_pk)
        amount = request.POST.get('amount')

        exist = ShoppingCartItem.objects.filter(cart__user = user).filter(product = product)

        # すでにカートに存在する商品の場合は個数をインクリメント
        if len(exist) > 0:
            current_amount = exist[0].amount
            exist[0].amount = current_amount + int(amount)
            exist[0].save()
        else:
            new_cart_item = ShoppingCartItem()
            new_cart_item.cart = request.user.cart
            new_cart_item.product = product
            new_cart_item.amount = int(amount)
            new_cart_item.save()
        return HttpResponseRedirect(reverse('amazon:cart',  kwargs={'pk': self.get_object().pk}))


def update_cart_item_amount(request):
    cart_item_pk = request.POST.get('cart_item_pk')
    new_amount = request.POST.get('amount')

    if cart_item_pk == None or new_amount == None:
        return JsonResponse({'error': 'invalid parameter'})
    if int(new_amount) <= 0:
        return JsonResponse({'error': 'amount must be greater than zero'})
    
    try:
        cart_item = ShoppingCartItem.objects.get(pk = cart_item_pk)
        cart_item.amount = int(new_amount)
        cart_item.save()
        print(cart_item.amount)
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e.args)})


def delete_cart_item(request):
    cart_item_pk = request.POST.get('cart_item_pk')
    if cart_item_pk == None:
        return JsonResponse({'error': 'invalid parameter'})
    try:
        cart_item = ShoppingCartItem.objects.get(pk = cart_item_pk)
        cart_item.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e.args)})