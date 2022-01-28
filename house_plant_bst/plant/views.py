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
        context['common_names'] = context['object'].get_common_names.all()
        return context
