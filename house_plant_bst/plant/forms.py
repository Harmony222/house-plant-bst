from django import forms
from .models import Plant, PlantCommonName
from django.forms import inlineformset_factory


class PlantCommonNameForm(forms.ModelForm):
    class Meta:
        model = PlantCommonName
        fields = [
            'name',
        ]


PlantCommonNameFormSet = inlineformset_factory(
    Plant,
    PlantCommonName,
    form=PlantCommonNameForm,
    fields=['name'],
    extra=4,
    can_delete=False,
)


class PlantForm(forms.ModelForm):
    class Meta:
        model = Plant
        fields = ['scientific_name', 'description', 'plant_care']
