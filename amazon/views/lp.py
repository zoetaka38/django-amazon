from django.views import generic

class Lp(generic.TemplateView):
    template_name = 'amazon/lp.html'