from django import forms


class TradeForm(forms.Form):
    username = forms.CharField(label='', max_length=150)


class MessageForm(forms.Form):
    message = forms.CharField(label='', max_length=1000)


class TradeResponseForm(forms.Form):
    RESPONSE_CHOICES = [('AC', 'Accept'),
                        ('RE', 'Reject')]
    trade_response = forms.CharField(label='Accept or Reject the request?',
                                     widget=forms
                                     .RadioSelect(choices=RESPONSE_CHOICES))
