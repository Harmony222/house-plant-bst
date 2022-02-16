from django.shortcuts import redirect, get_object_or_404, HttpResponse
from django.views.generic import (
    CreateView,
    ListView,
)
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q

from plant.mixins import TemplateTitleMixin
from order.models import Order, Address
from order.forms import OrderForm, OrderItemFormSet, AddressForm
from plant.models import UserPlant


class OrderCreateView(TemplateTitleMixin, CreateView, LoginRequiredMixin):
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
            context['order_item_form'] = OrderItemFormSet(self.request.POST)
        else:
            context['order_item_form'] = OrderItemFormSet()
        return context

    def get_form(self, *args, **kwargs):
        """Limits form address field to address's owned by user"""
        form = super(OrderCreateView, self).get_form(*args, **kwargs)
        form.fields[
            'address'
        ].queryset = self.request.user.get_user_addresses.all()
        return form

    def _calculate_total_price(self, quantity, order_item):
        return float(quantity * order_item.user_plant.unit_price)

    def form_valid(self, form):
        context = self.get_context_data()
        userplant_obj = context['userplant']

        # validate and save Order form
        if form.is_valid():
            order_obj = form.save(commit=False)
            order_obj.seller = userplant_obj.user
            order_obj.buyer = self.request.user
        order_obj.save()

        # validate and save OrderItem form
        order_item_form = context['order_item_form'][0]
        if order_item_form.is_valid():
            order_item_obj = order_item_form.save(commit=False)
            order_item_obj.order = order_obj
            order_item_obj.user_plant = userplant_obj
            order_item_obj.save()

        # reduce userplant quantity by ordered amount
        purchase_quantity = order_item_obj.quantity
        userplant_obj.quantity -= purchase_quantity
        userplant_obj.save()

        # add order total to order
        order_obj.total_price = self._calculate_total_price(
            purchase_quantity, order_item_obj
        )
        order_obj.save()
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('order:user_orders_all')


class AddressCreateView(TemplateTitleMixin, CreateView, LoginRequiredMixin):
    model = Address
    title = "Address create"
    form_class = AddressForm
    template_name = 'order/address_create.html'
    success_url = None

    def form_valid(self, form):
        if form.is_valid():
            address_obj = form.save(commit=False)
            address_obj.user = self.request.user
            address_obj.save()

            # https://stackoverflow.com/questions/14782460/how-can-i-close-a-popup-and-redirect-to-another-page-in-a-django-view
            return HttpResponse(
                '<script type="text/javascript">'
                'window.close(); '
                'window.parent.location.href = window.parent.location.href;'
                '</script>'
            )

    def get_success_url(self):
        return reverse_lazy('plant:marketplace_plants')


class UserOrderListView(TemplateTitleMixin, ListView, LoginRequiredMixin):
    model = Order
    title = 'User Orders'
    template_name = 'order/user_order_list.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(
            Q(seller=self.request.user) | Q(buyer=self.request.user)
        )
