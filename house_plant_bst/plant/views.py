# from django.shortcuts import render
from django.views.generic import ListView, DetailView

from .models import Plant, PlantCommonName
from .mixins import TemplateTitleMixin


class PlantListView(TemplateTitleMixin, ListView):
    model = Plant
    title = 'Plants'


class PlantDetailView(TemplateTitleMixin, DetailView):
    model = Plant
    title = 'Plant Detail'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['title'] = self.get_title()
        url_params = self.kwargs
        pk = url_params.get('pk')
        qs = PlantCommonName.objects.filter(plant=pk)
        # print(qs)
        context['common_names'] = qs
        return context
