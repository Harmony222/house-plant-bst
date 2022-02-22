from django import forms
from django.forms import inlineformset_factory
from django.db import models

from order.models import Order, Address, OrderItem


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['street', 'city', 'state', 'zip']


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['handling', 'address_for_shipping', 'address_for_pickup']
        widgets = {
            'handling': forms.RadioSelect(),
        }


class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['quantity']

    quantity = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'id': 'quantity_field',
                'min': 1,
                'max': 5,
                'type': 'number',
                'class': 'form-control',
                'value': 1,
            }
        )
    )


OrderItemFormSet = inlineformset_factory(
    Order,
    OrderItem,
    form=OrderItemForm,
    fields=['quantity'],
    extra=1,
    max_num=1,
    can_delete=False,
)
