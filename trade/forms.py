from django import forms
from plant.models import UserPlant
from django.utils.safestring import mark_safe
from django.templatetags.static import static


class MessageForm(forms.Form):
    message = forms.CharField(label='', max_length=1000)


class TradeResponseForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.items = kwargs.pop('items', None)
        self.is_offered_for_shipping = kwargs.pop(
                                       'is_offered_for_shipping', None)
        self.is_offered_for_pickup = kwargs.pop(
                                     'is_offered_for_pickup', None)
        self.seller_plant = kwargs.pop('seller_plant', None)
        super(TradeResponseForm, self).__init__(*args, **kwargs)
        self.RESPONSE_CHOICES = [(
            'AC ' + str(item.id),
            'Accept ' + str(item.user_plant.plant.scientific_name)
        ) for item in self.items]
        self.RESPONSE_CHOICES.append(('RE', 'Reject'))
        self.fields['trade_response'] = forms.CharField(
            widget=forms.RadioSelect(
                choices=self.RESPONSE_CHOICES,
                attrs={'onchange': 'show_handling();'}
            ),
        )
        self.ACCEPTED_HANDLING_METHOD_CHOICES = []
        # prefill default handling method if seller didn't specify handling or
        # if there are two handling methods offered by the user:
        if self.is_offered_for_pickup:
            self.ACCEPTED_HANDLING_METHOD_CHOICES.append(
                ('PI', 'Pickup'))
        if self.is_offered_for_shipping:
            self.ACCEPTED_HANDLING_METHOD_CHOICES.append(
                ('SH', 'Shipping'))
        if len(self.ACCEPTED_HANDLING_METHOD_CHOICES) > 1:
            self.fields['handling_methods'] = forms.CharField(
                label='Choose a handling_method:',
                widget=forms
                .RadioSelect(
                    choices=self.ACCEPTED_HANDLING_METHOD_CHOICES
                ),
                required=True
            )
        else:
            self.fields['handling_methods'] = forms.CharField(
                widget=forms.RadioSelect(
                    choices=self.ACCEPTED_HANDLING_METHOD_CHOICES
                ),
                required=True,
                initial=self.ACCEPTED_HANDLING_METHOD_CHOICES[0][0]
            )


class NameChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, user_plant_obj):
        return mark_safe(_card_html_builder(user_plant_obj))


class TradeForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.seller_plant = kwargs.pop('seller_plant', None)
        self.is_for_shipping = kwargs.pop('is_for_shipping', None)
        self.is_for_pickup = kwargs.pop('is_for_pickup', None)
        self.show_address_fields = False
        super(TradeForm, self).__init__(*args, **kwargs)

        self.fields['seller_plant'] = forms.ModelChoiceField(
            widget=forms.HiddenInput,
            required=True,
            queryset=UserPlant.objects.filter(pk=self.seller_plant.id),
            initial=self.seller_plant
        )

        self.fields['user_plants_for_trade'] = NameChoiceField(
            widget=forms.CheckboxSelectMultiple,
            queryset=UserPlant.objects.filter(
                user=self.user,
                quantity__gt=0,
                deleted_by_user=False
            )
        )
        handling_is_unspecified = not (self.seller_plant.is_for_shipping or \
                                  self.seller_plant.is_for_pickup)
        if self.is_for_shipping or handling_is_unspecified:
            self.handling_options = [
                ('shipping_choice', 'Shipping')
            ]
            if self.is_for_pickup or handling_is_unspecified:
                # if the plant is being offered for both shipping and pickup,
                # the trade requester needs to specify either or both.
                self.handling_options.append(('pickup_choice', 'Pickup'))
                self.fields['handling_methods'] = forms.MultipleChoiceField(
                    required=True,
                    widget=forms.CheckboxSelectMultiple,
                    choices=self.handling_options
                )
            else:
                # if the plant is offered only for shipping, default to
                # shipping and make the field hidden
                self.fields['handling_methods'] = forms.ChoiceField(
                    widget=forms.HiddenInput,
                    required=True,
                    choices=self.handling_options,
                    initial=self.handling_options[0][0]
                )
            self.fields['handling_methods'].label = ''
        if self.is_for_shipping or handling_is_unspecified:
            # add the addresses field for any shipping handling method
            self.fields['addresses'] = forms.ModelChoiceField(
                label='Choose a shipping address:',
                widget=forms.Select,
                queryset=self.user.get_user_addresses.all(),
                required=False
            )
            self.fields['addresses'].label = ''
        self.fields['user_plants_for_trade'].label = ''


def _card_html_builder(user_plant_obj):
    image_url = user_plant_obj.image_url if user_plant_obj.image_url \
                else static('images/default_userplant_image.png')
    image_html_element = '<img class ="card-img-top create-trade-plant-img"'\
                         f'src="{image_url}" alt=\"Card image cap\">'
    owner = user_plant_obj.user.username.capitalize()
    location = user_plant_obj.user.location.capitalize()
    tags = user_plant_obj.tags.all()
    tags_html = ''
    if tags:
        for tag in tags:
            tags_html += '<span class ="badge rounded-pill bg-light'\
                         f' text-dark fw-light"> {tag.name} </span >'
    card_html_element = \
        '<div class ="card-body" >'\
        '<h5 class ="card-subtitle my-1" style="display: inline-block;'\
        'white-space: nowrap;">' \
        '<!-- Placeholder tags -->' \
        '<div class ="tags my-2" >' \
        f'{tags_html}' \
        '</div>'\
        '<!-- Scientific name links to userplant detail page -->'\
        f'{user_plant_obj.plant.scientific_name.capitalize()}'\
        '</a>'\
        '</h5>' \
        '<!-- For trade items, don\'t show the unit price -->' \
        '<!-- Seller and location info -->'\
        f'<p class ="plant-card-text" > Owner: {owner} <br>'\
        f'Location: {location} </p>' \
        '<!-- Don\'t show Buy / Trade / Info since all plants in this list'\
        'are for trade-->'\
        '</div>'
    return image_html_element + card_html_element
