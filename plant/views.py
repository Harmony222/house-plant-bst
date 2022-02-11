from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.conf import settings
from django.shortcuts import redirect

import json
import os

from .models import Plant, UserPlant, Tag
from .mixins import TemplateTitleMixin
from .forms import PlantCommonNameFormSet, PlantForm, UserPlantForm, TagFormSet


##########################################################################
# Plant Views


class PlantListView(TemplateTitleMixin, ListView):
    model = Plant
    title = 'Plants'
    paginate_by = 8
    ordering = ['id']

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

    def get_queryset(self):
        """Sort queryset by plant name"""
        query_set = super().get_queryset().order_by('scientific_name')
        return query_set


class PlantDetailView(TemplateTitleMixin, DetailView):
    model = Plant
    title = 'Plant Detail'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['title'] = self.get_title()
        context['common_names'] = context['object'].get_common_names.all()
        return context


class PlantCreateView(TemplateTitleMixin, LoginRequiredMixin, CreateView):
    model = Plant
    form_class = PlantForm
    template_name = 'plant/plant_create.html'
    success_url = None
    title = "Add New"

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


class PlantUpdateView(TemplateTitleMixin, LoginRequiredMixin, UpdateView):
    form_class = PlantForm
    model = Plant
    template_name = 'plant/plant_create.html'
    title = "Update"

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

    def get_context_data(self, *args, **kwargs):
        """Creates context data for UserPlant.

        Adds a list of objects to context, each object contains UserPlant
        object and User's location based on zipcode
        """
        context = super().get_context_data(*args, **kwargs)
        userplant_list = []
        if settings.DEBUG:
            file_path = os.path.join(settings.STATIC_ROOT, 'zipcode_data.json')
        else:
            file_path = 'static/zipcode_data.json'
        zipcode_file = open(file_path)
        zipcode_data = json.load(zipcode_file)
        for userplant in context['object_list']:
            if userplant.user is not None:
                zipcode = userplant.user.location
                if zipcode in zipcode_data:
                    city_state = (
                        f'{zipcode_data[zipcode]["city"]}, '
                        f'{zipcode_data[zipcode]["state"]}'
                    )
                else:
                    city_state = "Contact seller"
                userplant_list.append(
                    {'userplant': userplant, 'location': city_state}
                )
        context['object_list'] = userplant_list
        context['marketplace'] = True
        return context

    def get_queryset(self):
        """Restrict queryset to:

        - exclude deleted UserPlants
        """
        return UserPlant.objects.filter(deleted_by_user=False, quantity__gt=0)


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
        """Restrict queryset to:

        - include only the user's UserPlants
        - exclude UserPlants deleted by the user
        """
        return UserPlant.objects.filter(
            user=self.request.user, deleted_by_user=False
        )


class UserPlantDetailView(LoginRequiredMixin, TemplateTitleMixin, DetailView):
    model = UserPlant
    title = 'Signed in User Plant detail'
    template_name = 'plant/userplant/userplant_detail.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        return context


class UserPlantCreateView(TemplateTitleMixin, LoginRequiredMixin, CreateView):
    form_class = UserPlantForm
    model = UserPlant
    template_name = 'plant/userplant/userplant_create.html'
    title = "Add New"

    def get_success_url(self):
        return reverse_lazy('plant:userplant_all')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        if self.request.POST:
            context['tag_form'] = TagFormSet(self.request.POST)
        else:
            context['tag_form'] = TagFormSet(queryset=Tag.objects.none())
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        tag_form = context['tag_form']

        # have to save userplant object before adding extra tags
        userplant_object = form.save()
        userplant_object.user = self.request.user
        if tag_form.is_valid():
            # tag_form.instance = userplant_object
            tag_obj = tag_form.save()
            for tag in tag_obj:
                userplant_object.tags.add(tag)
        userplant_object.save()

        return redirect(self.get_success_url())


class UserPlantUpdateView(TemplateTitleMixin, LoginRequiredMixin, UpdateView):
    form_class = UserPlantForm
    model = UserPlant
    template_name = 'plant/userplant/userplant_create.html'
    title = "Update"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['update'] = True
        if self.request.POST:
            context['tag_form'] = TagFormSet(self.request.POST)
        else:
            context['tag_form'] = TagFormSet(queryset=Tag.objects.none())
        return context

    def get_success_url(self):
        return reverse_lazy('plant:userplant_all')

    def form_valid(self, form):
        context = self.get_context_data()
        tag_form = context['tag_form']
        # have to save userplant object before adding extra tags
        userplant_object = form.save()
        userplant_object.user = self.request.user
        if tag_form.is_valid():
            tag_obj = tag_form.save()
            for tag in tag_obj:
                userplant_object.tags.add(tag)
        userplant_object.save()
        return redirect(self.get_success_url())


class UserPlantDeleteView(LoginRequiredMixin, DeleteView):
    model = UserPlant
    template_name = 'forms_delete.html'
    success_url = reverse_lazy('plant:userplant_all')

    def form_valid(self, form):
        """Set UserPlant deleted_by_user field to True"""
        self.object.deleted_by_user = True
        self.object.save()
        return redirect(self.success_url)
