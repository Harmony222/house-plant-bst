from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic import (
    CreateView,
)
from django.urls import reverse_lazy

from plant.mixins import TemplateTitleMixin
from order.models import Order, Address
from order.forms import OrderForm, AddressFormSet, OrderItemFormSet
from plant.models import UserPlant


def order_plant(request, pk):
    context = {'pk': pk}
    return render(request, 'order/order_plant.html', context)


class OrderCreateView(TemplateTitleMixin, CreateView):
    model = Order
    title = "Order"
    form_class = OrderForm
    template_name = 'order/order_create.html'
    success_url = None

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        userplant_pk = self.kwargs['userplant_pk']
        userplant = get_object_or_404(UserPlant, pk=userplant_pk)
        context['userplant'] = userplant
        if self.request.POST:
            context['address_form'] = AddressFormSet(self.request.POST)
            context['order_item_form'] = OrderItemFormSet(self.request.POST)
        else:
            context['address_form'] = AddressFormSet(
                queryset=Address.objects.none()
            )
            context['order_item_form'] = OrderItemFormSet()
        print("context from get_context_data", context)
        return context

    def _calculate_total_price(self, quantity, order_item):
        return float(quantity * order_item.price)

    def form_valid(self, form):
        context = self.get_context_data()
        print("context form form_valid", context)
        userplant_obj = context['userplant']
        if form.is_valid():
            print("test form valid")
            order_obj = form.save(commit=False)
            print(order_obj)
            order_obj.seller = userplant_obj.user
            order_obj.buyer = self.request.user

        address_form = context['address_form'][0]
        if address_form.is_valid():
            address_obj = address_form.save()
            order_obj.address = address_obj

        order_obj.save()
        order_item_form = context['order_item_form'][0]
        if order_item_form.is_valid():
            print("order item form is valid")
            order_item_obj = order_item_form.save(commit=False)
            order_item_obj.order = order_obj
            order_item_obj.user_plant = userplant_obj
            order_item_obj.save()
            print(order_item_obj)

        else:
            print("NOT VALID")
        return redirect(self.get_success_url())
        # return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('plant:marketplace_plants')
