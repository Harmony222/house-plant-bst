from django.http import Http404
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist


from .models import Plant, UserPlant, Tag
from .mixins import TemplateTitleMixin, ZipcodeCityStateMixin
from .forms import PlantCommonNameFormSet, PlantForm, UserPlantForm, TagFormSet


##########################################################################
# Plant Views


class PlantListView(TemplateTitleMixin, ListView):
    model = Plant
    title = 'Plants'
    paginate_by = 8
    ordering = ['id']

    def get_queryset(self):
        """Sort queryset by plant name"""
        query_set = super().get_queryset().order_by('scientific_name')
        return query_set


class PlantDetailView(TemplateTitleMixin, DetailView):
    model = Plant
    title = 'Plant Detail'


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


class MarketplacePlantListView(
    TemplateTitleMixin, ZipcodeCityStateMixin, ListView
):
    model = UserPlant
    title = 'Marketplace Plants'
    template_name = 'plant/userplant/userplant_list.html'

    def _get_all_tags_assigned_to_userplants(self):
        """Get all tags that have been assigned to a UserPlant"""
        queryset = Tag.objects.all().filter(userplant__isnull=False)
        return queryset.distinct().order_by('name')

    def get_context_data(self, *args, **kwargs):
        """Creates context data for UserPlant.

        Adds a list of objects to context, each object contains UserPlant
        object and User's location based on zipcode
        """
        context = super().get_context_data(*args, **kwargs)
        userplant_list = []
        zipcode_data = self._get_zipcode_data()
        for userplant in context['object_list']:
            city_state = self._get_citystate_from_zipcode(
                userplant.user.location, zipcode_data
            )
            userplant_list.append(
                {'userplant': userplant, 'location': city_state}
            )
        context['object_list'] = userplant_list
        context['marketplace'] = True
        context['tags'] = self._get_all_tags_assigned_to_userplants()
        # print(context)
        return context

    def get_queryset(self, *args, **kwargs):
        """Restrict queryset to:

        - exclude deleted UserPlants
        - exclude plants with quantity of zero
        - if tags query params provided, return only those plants with tags
        """
        queryset = super().get_queryset()
        queryset = queryset.filter(deleted_by_user=False, quantity__gt=0)
        tags = self.request.GET.get('tags')
        shipping = self.request.GET.get('shipping')
        pickup = self.request.GET.get('pickup')
        if tags:
            tag_ids = [int(str_pk) for str_pk in tags.split(',')]
            queryset = queryset.filter(tags__id__in=tag_ids)
        if shipping:
            queryset = queryset.filter(is_for_shipping=True)
        if pickup:
            queryset = queryset.filter(is_for_pickup=True)
        return queryset


class MarketplacePlantDetailView(
    TemplateTitleMixin, ZipcodeCityStateMixin, DetailView
):
    model = UserPlant
    title = 'Marketplace Plant Detail'
    template_name = 'plant/userplant/userplant_detail.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['marketplace'] = True
        zipcode = context['object'].user.location
        zipcode_data = self._get_zipcode_data()
        context['location'] = self._get_citystate_from_zipcode(
            zipcode, zipcode_data
        )

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
        queryset = UserPlant.objects.filter(
            user=self.request.user, deleted_by_user=False
        )
        tags = self.request.GET.get('tags')
        shipping = self.request.GET.get('shipping')
        pickup = self.request.GET.get('pickup')
        if tags:
            tag_ids = [int(str_pk) for str_pk in tags.split(',')]
            queryset = queryset.filter(tags__id__in=tag_ids)
        if shipping:
            queryset = queryset.filter(is_for_shipping=True)
        if pickup:
            queryset = queryset.filter(is_for_pickup=True)
        return queryset


class UserPlantDetailView(LoginRequiredMixin, TemplateTitleMixin, DetailView):
    model = UserPlant
    title = 'Signed in User Plant detail'
    template_name = 'plant/userplant/userplant_detail.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['marketplace'] = False
        return context

    def get_object(self, queryset=None):
        """raise 404 error if UserPlant does not belong to signed-in user"""
        obj = super().get_object(queryset)
        if obj.user != self.request.user:
            raise Http404("UserPlant not found for signed-in user")
        return obj


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
            # set qeuryset to none so that the form is not prepopulated
            # with Tag objects
            context['tag_form'] = TagFormSet(queryset=Tag.objects.none())
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        tag_forms = context['tag_form']
        # have to save userplant object before adding extra tags
        userplant_object = form.save()
        userplant_object.user = self.request.user
        for tag_form in tag_forms:
            if tag_form.is_valid():
                tag_name = tag_form.cleaned_data.get('name')
                if tag_name is not None:
                    # try getting object with tag name, if Tag exists, use
                    # existing Tag, otherwise create new Tag object
                    try:
                        tag_obj = Tag.objects.get(name=tag_name)
                    except ObjectDoesNotExist:
                        tag_obj = tag_form.save()
                    userplant_object.tags.add(tag_obj)

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

    def get_object(self, queryset=None):
        """raise 404 error if UserPlant does not belong to signed-in user"""
        obj = super().get_object(queryset)
        if obj.user != self.request.user:
            raise Http404("UserPlant not found for signed-in user")
        return obj


class UserPlantDeleteView(LoginRequiredMixin, DeleteView):
    model = UserPlant
    template_name = 'forms_delete.html'
    success_url = reverse_lazy('plant:userplant_all')

    def form_valid(self, form):
        """Set UserPlant deleted_by_user field to True
        (does not delete UserPlant from database)
        """
        self.object.deleted_by_user = True
        self.object.save()
        return redirect(self.success_url)

    def get_object(self, queryset=None):
        """raise 404 error if UserPlant does not belong to signed-in user"""
        obj = super().get_object(queryset)
        if obj.user != self.request.user:
            raise Http404("UserPlant not found for signed-in user")
        return obj
