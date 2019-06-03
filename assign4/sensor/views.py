from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from django.db.models import Q
from .models import Distance

# Create your views here.
class HomePageView(TemplateView):
    template_name = 'home.html'

class SearchResultsView(ListView):
    model = Distance
    template_name = 'search_results.html'

    def get_queryset(self):
        query = self.request.GET.get('q')
        object_list = Distance.objects.filter(Q(distance=query))
        return object_list