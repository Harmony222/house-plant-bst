from django import forms
from .models import Plant, PlantCommonName, UserPlant
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
    extra=1,
    can_delete=True,
)


class PlantForm(forms.ModelForm):
    class Meta:
        model = Plant
        fields = ['scientific_name', 'description', 'plant_care']


class UserPlantForm(forms.ModelForm):
    class Meta:
        model = UserPlant
        fields = [
            'plant',
            'is_for_sale',
            'is_for_trade',
            'is_for_pickup',
            'is_for_shipping',
            'image_url',
            'quantity',
            'unit_price',
            'comment',
        ]

    def __init__(self, *args, **kwargs):
        super(UserPlantForm, self).__init__(*args, **kwargs)
        self.fields['plant'].queryset = self.fields['plant'].queryset.order_by(
            'scientific_name'
        )
