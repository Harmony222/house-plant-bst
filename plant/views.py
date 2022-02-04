from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

# import json
from .models import Plant, UserPlant
from .mixins import TemplateTitleMixin
from .forms import PlantCommonNameFormSet, PlantForm, UserPlantForm


##########################################################################
# Plant Views


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
        # print(context)
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
        return self.object.get_absolute_url()


class PlantUpdateView(LoginRequiredMixin, UpdateView):
    form_class = PlantForm
    model = Plant
    template_name = 'plant/plant_create.html'

    def get_context_data(self, **kwargs):
        context = super(PlantUpdateView, self).get_context_data(**kwargs)
        if self.request.POST:
            context['common_names_form'] = PlantCommonNameFormSet(
                self.request.POST, instance=self.object
            )
        else:
            context['common_names_form'] = PlantCommonNameFormSet(
                instance=self.object
            )
        context['update'] = True
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        common_names_form = context['common_names_form']
        if common_names_form.is_valid():
            self.object = form.save()
            common_names_form.instance = self.object
            common_names_form.save()
        return super(PlantUpdateView, self).form_valid(form)

    def get_success_url(self):
        return self.object.get_absolute_url()


class PlantDeleteView(LoginRequiredMixin, DeleteView):
    model = Plant
    template_name = 'forms_delete.html'
    success_url = reverse_lazy('plant:all_plants')


##########################################################################
# UserPlant Views for MarketPlace


class MarketplacePlantListView(TemplateTitleMixin, ListView):
    model = UserPlant
    title = 'Marketplace Plants'
    template_name = 'plant/userplant/userplant_list.html'
    # template_name = 'plant/marketplace_plant_list.html'

    def get_context_data(self, *args, **kwargs):
        """Creates context data for UserPlant.

        Adds a list of objects to context, each object contains UserPlant
        object and User's location based on zipcode
        """
        context = super().get_context_data(*args, **kwargs)
        userplant_list = []
        # zipcode_file = open('static/zipcode_data.json')
        # zipcode_data = json.load(zipcode_file)
        for userplant in context['object_list']:
            zipcode = userplant.user.location
            # if zipcode in zipcode_data:
            #     city_state = (
            #         f'{zipcode_data[zipcode]["city"]}, '
            #         f'{zipcode_data[zipcode]["state"]}'
            #     )
            # else:
            #     city_state = "Contact seller"
            city_state = zipcode
            userplant_list.append(
                {'userplant': userplant, 'location': city_state}
            )
        context['object_list'] = userplant_list
        context['marketplace'] = True
        return context


class MarketplacePlantDetailView(TemplateTitleMixin, DetailView):
    model = UserPlant
    title = 'Market Place Plant Detail'
    template_name = 'plant/userplant/userplant_detail.html'
    # template_name = 'plant/marketplace_plant_detail.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['marketplace'] = True
        return context


##########################################################################
# UserPlant Views For Signed in User


class UserPlantListView(
    MarketplacePlantListView, LoginRequiredMixin, TemplateTitleMixin, ListView
):
    model = UserPlant
    title = "Signed in User's Plants"
    template_name = 'plant/userplant/userplant_list.html'

    def get_context_data(self, *args, **kwargs):
        """Extends functionality of MarketplacePlantListView

        Sets marketplace flag to False
        """
        context = super().get_context_data(*args, **kwargs)
        context['marketplace'] = False
        return context

    def get_queryset(self):
        """Restrict queryset to only the user's UserPlants"""
        return UserPlant.objects.filter(user=self.request.user)


class UserPlantDetailView(LoginRequiredMixin, TemplateTitleMixin, DetailView):
    model = UserPlant
    title = 'Signed in User Plant detail'
    template_name = 'plant/userplant/userplant_detail.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        print(context)
        return context


class UserPlantCreateView(LoginRequiredMixin, CreateView):
    form_class = UserPlantForm
    model = UserPlant
    template_name = 'plant/userplant/userplant_create.html'

    def get_success_url(self):
        return reverse_lazy('plant:userplant_all')

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.user = self.request.user
        obj.save()
        return super().form_valid(form)


class UserPlantUpdateView(LoginRequiredMixin, UpdateView):
    form_class = UserPlantForm
    model = UserPlant
    template_name = 'plant/userplant/userplant_create.html'

    def get_success_url(self):
        return reverse_lazy('plant:userplant_all')

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.user = self.request.user
        obj.save()
        return super().form_valid(form)
