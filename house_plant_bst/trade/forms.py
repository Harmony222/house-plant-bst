from django import forms


class ThreadForm(forms.Form):
  username = forms.CharField(label='', max_length=150)


class MessageForm(forms.ModelForm):
    message = forms.CharField(label='', max_length=1000)