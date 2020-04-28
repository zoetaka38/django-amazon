from ..models import Product
from django.views import generic


class ItemList(generic.ListView):
    model = Product
    template_name = 'amazon/item_list.html'
    def get_queryset(self):
        products = Product.objects.all()
        if 'q' in self.request.GET and self.request.GET['q'] != None:
            q = self.request.GET['q']
            products = products.filter(name__icontains = q)

        return products


class ItemDetail(generic.DetailView):
    model = Product
    template_name = 'amazon/item_detail.html'