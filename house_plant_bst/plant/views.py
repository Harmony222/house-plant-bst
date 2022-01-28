# from django.shortcuts import render
from django.views.generic import ListView, DetailView

from .models import Plant
from .mixins import TemplateTitleMixin


class PlantListView(TemplateTitleMixin, ListView):
    model = Plant
    title = 'Plants'

    # def get_queryset(self):
    #     qs = self.model.objects.all().plantcommonname_set.all()
    #     print(qs)
    #     return qs

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['title'] = self.get_title()
        # print(context)
        for sci_plant in context['object_list']:
            sci_plant['test'] = 'test'
            # sci_plant['common_names']
            # sci_plant['common_name'] = PlantCommonName.objects.filter(
            #     plant=sci_plant.pk
            # )
            print(sci_plant)

        return context


class PlantDetailView(TemplateTitleMixin, DetailView):
    model = Plant
    title = 'Plant Detail'

    # def get_queryset(self):
    #     url_pk = self.kwargs.get('pk')
    #     qs = self.model.objects.get(pk=url_pk).get_common_names.all()
    #     print(qs)
    #     return qs

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['title'] = self.get_title()
        context['common_names'] = context['object'].get_common_names.all()
        return context
