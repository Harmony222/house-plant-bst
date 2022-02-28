from django import forms
from django.forms import HiddenInput, inlineformset_factory

from order.models import Order, Address, OrderItem


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['street', 'city', 'state', 'zip']


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['handling', 'address_for_shipping']
        widgets = {
            'handling': forms.RadioSelect(),
        }

    def clean(self):
        super().clean()
        shipping_selected = self.cleaned_data['handling'] == 'SH'
        if shipping_selected:
            address = self.cleaned_data['address_for_shipping']
            if address is None:
                raise forms.ValidationError(
                    'Shipping is selected - please enter shipping address'
                )


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


class SellerOrderForm(forms.ModelForm):
    """Used in order detail view for seller to update order status and
    pickup address"""

    class Meta:
        model = Order
        fields = ['handling', 'address_for_pickup', 'status']

    def __init__(self, *args, **kwargs):
        super(SellerOrderForm, self).__init__(*args, **kwargs)
        self.fields['status'].widget = HiddenInput(
            attrs={'id': 'status_field'}
        )
        self.fields['handling'].widget = HiddenInput()
