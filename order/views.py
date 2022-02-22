from django.shortcuts import redirect, get_object_or_404, HttpResponse
from django.http import Http404
from django.views.generic import (
    CreateView,
    ListView,
    DetailView,
    UpdateView,
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
    title = "Order Plant"
    form_class = OrderForm
    template_name = 'order/order_create.html'
    success_url = None

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        userplant_pk = self.kwargs['userplant_pk']
        userplant = get_object_or_404(UserPlant, pk=userplant_pk)
        context['userplant'] = userplant
        context['total_quantity'] = userplant.quantity
        if self.request.POST:
            context['order_item_form'] = OrderItemFormSet(self.request.POST)
        else:
            context['order_item_form'] = OrderItemFormSet()
        return context

    def get_form(self, *args, **kwargs):
        """Limits form address field to address's owned by user"""
        form = super(OrderCreateView, self).get_form(*args, **kwargs)
        form.fields[
            'address_for_shipping'
        ].queryset = self.request.user.get_user_addresses.all()
        return form

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
        order_obj.total_price = order_obj.calculate_total_price()

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
    title = 'User Purchase Order History'
    template_name = 'order/user_order_list.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(
            Q(seller=self.request.user) | Q(buyer=self.request.user)
        )


class BuyerOrderDetailView(
    TemplateTitleMixin,
    DetailView,
    LoginRequiredMixin,
):
    model = Order
    title = 'Buyer Order Detail'
    template_name = 'order/buyer_order_detail.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        order = context['object']
        context['total_num_items'] = order.get_total_num_items()
        return context

    def get_object(self, queryset=None):
        """Raise 404 error if User is not Order Buyer"""
        obj = super().get_object(queryset)
        if obj.buyer != self.request.user:
            raise Http404("Order number not found for signed-in user")
        return obj


class BuyerOrderUpdateView(
    TemplateTitleMixin,
    UpdateView,
    LoginRequiredMixin,
):
    model = Order
    title = 'Update Order'
    form_class = OrderForm
    template_name = 'order/order_create.html'
    # template_name = 'order/buyer_order_update.html'
    success_url = None

    def get_object(self, queryset=None):
        """Raise 404 error if User is not Order Buyer"""
        obj = super().get_object(queryset)
        if obj.buyer != self.request.user:
            raise Http404("Order number not found for signed-in user")
        return obj

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        # total quantity available for Buyer is the quantity they have
        # currently ordered plus the quantity remaining in UserPlant
        userplant_pk = self.object.get_order_items.all()[0].user_plant.pk
        userplant = get_object_or_404(UserPlant, pk=userplant_pk)
        curr_quantity_ordered = self.object.get_order_items.all()[0].quantity
        curr_quantity_left = userplant.quantity
        total_quantity_available = curr_quantity_ordered + curr_quantity_left
        context['userplant'] = userplant
        context['total_quantity'] = total_quantity_available

        if self.request.POST:
            context['order_item_form'] = OrderItemFormSet(
                self.request.POST, instance=self.object
            )
        else:
            context['order_item_form'] = OrderItemFormSet(instance=self.object)
        context["update"] = True
        return context

    def get_form(self, *args, **kwargs):
        """Limits form address field to address's owned by user"""
        form = super(BuyerOrderUpdateView, self).get_form(*args, **kwargs)
        form.fields[
            'address_for_shipping'
        ].queryset = self.request.user.get_user_addresses.all()
        return form

    def form_valid(self, form):
        context = self.get_context_data()

        order_item_form = context['order_item_form'][0]
        if form.is_valid():
            order_obj = form.save()
        if order_item_form.is_valid():
            order_item_obj = order_item_form.save()
        else:
            print(order_item_form.errors.as_data())

        # adjust userplant quantity by adjusted amount
        purchase_quantity = order_item_obj.quantity
        userplant_obj = context['userplant']
        userplant_obj.quantity = context['total_quantity'] - purchase_quantity
        userplant_obj.save()

        # add order total to order
        order_obj.total_price = order_obj.calculate_total_price()

        return super(BuyerOrderUpdateView, self).form_valid(form)

    def get_success_url(self) -> str:
        return reverse_lazy(
            'order:buyer_order_detail', kwargs={'pk': self.object.pk}
        )
