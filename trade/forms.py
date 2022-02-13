from django import forms
from plant.models import UserPlant


class NameChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return f'{obj.plant.scientific_name}'


class TradeForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(TradeForm, self).__init__(*args, **kwargs)

        self.fields['user_plants_for_trade'] = NameChoiceField(
            widget=forms.CheckboxSelectMultiple,
            queryset=UserPlant.objects.filter(
                user=self.user,
                is_for_trade=True,
                quantity__gt=0,
            )
        )

        self.fields['user_plants_for_trade'].label = ''


class MessageForm(forms.Form):
    message = forms.CharField(label='', max_length=1000)


class TradeResponseForm(forms.Form):
    RESPONSE_CHOICES = [('AC', 'Accept'),
                        ('RE', 'Reject')]
    trade_response = forms.CharField(
        label='Accept or Reject the request?',
        widget=forms
        .RadioSelect(choices=RESPONSE_CHOICES)
    )