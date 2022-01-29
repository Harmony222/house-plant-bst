from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

from .models import Plant
from .mixins import TemplateTitleMixin
from .forms import PlantCommonNameFormSet, PlantForm


class PlantListView(TemplateTitleMixin, ListView):
    model = Plant
    title = 'Plants'

    def get_context_data(self, *args, **kwargs):
        """Creates context data.

        Adds title to context.
        Adds a list of objects to context, each object contains Plant object
        and list of Plant's common names
        """
        context = super().get_context_data(*args, **kwargs)
        context['title'] = self.get_title()
        plant_list = []
        for plant in context['object_list']:
            names = plant.get_common_names.all()
            common_names = []
            for name in names:
                common_names.append(name.name)
            plant_list.append({'plant': plant, 'common_names': common_names})

        context['object_list'] = plant_list
        return context


class PlantDetailView(TemplateTitleMixin, DetailView):
    model = Plant
    title = 'Plant Detail'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['title'] = self.get_title()
        context['common_names'] = context['object'].get_common_names.all()
        return context


class PlantCreateView(LoginRequiredMixin, CreateView):
    model = Plant
    form_class = PlantForm
    template_name = 'plant/plant_create.html'
    success_url = None

    def get_context_data(self, **kwargs):
        context = super(PlantCreateView, self).get_context_data(**kwargs)
        if self.request.POST:
            context['common_names_form'] = PlantCommonNameFormSet(
                self.request.POST
            )
        else:
            context['common_names_form'] = PlantCommonNameFormSet()
        print(context)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        common_names_form = context['common_names_form']
        if common_names_form.is_valid():
            self.object = form.save()
            common_names_form.instance = self.object
            common_names_form.save()
        return super(PlantCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'plant:plant_detail', kwargs={'pk': self.object.pk}
        )
