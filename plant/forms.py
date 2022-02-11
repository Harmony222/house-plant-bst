from django import forms
from .models import Plant, PlantCommonName, UserPlant, Tag
from django.forms import modelformset_factory, inlineformset_factory


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
            'tags',
        ]

    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all().order_by('name'),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super(UserPlantForm, self).__init__(*args, **kwargs)
        self.fields['plant'].queryset = self.fields['plant'].queryset.order_by(
            'scientific_name'
        )


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = [
            'name',
        ]


TagFormSet = modelformset_factory(
    Tag,
    form=TagForm,
    fields=['name'],
    # form does not work when extra=1 and you add use + button
    extra=2,
    can_delete=True,
)
