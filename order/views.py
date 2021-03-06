from django.shortcuts import redirect, get_object_or_404, HttpResponse
from django.http import Http404
from django.views.generic import (
    CreateView,
    ListView,
    DetailView,
    UpdateView,
    DeleteView,
)
from django.views.generic.edit import ModelFormMixin
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone

from plant.mixins import TemplateTitleMixin
from order.models import Order, Address
from order.forms import (
    OrderForm,
    OrderItemFormSet,
    AddressForm,
    SellerOrderForm,
)
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
        """Set form fields based on User and UserPlant attributes

        - Limits form address field to address's owned by user
        - Limits Handling field options to UserPlant handling options
        """
        form = super(OrderCreateView, self).get_form(*args, **kwargs)
        form.fields[
            'address_for_shipping'
        ].queryset = self.request.user.get_user_addresses.all()

        # set Order form Handling field based on UserPlant handling options
        # Handling default includes both shipping and pickup options
        userplant_pk = self.kwargs['userplant_pk']
        userplant = get_object_or_404(UserPlant, pk=userplant_pk)
        if userplant.is_for_shipping and not userplant.is_for_pickup:
            form.fields['handling'].choices = [('SH', 'Shipping')]
        if not userplant.is_for_shipping and userplant.is_for_pickup:
            form.fields['handling'].choices = [('PI', 'Pickup')]
            form.fields['handling'].initial = 'PI'

        return form

    def form_valid(self, form):
        context = self.get_context_data()
        userplant_obj = context['userplant']

        order_item_form = context['order_item_form'][0]
        # validate and save Order form
        if form.is_valid():
            order_obj = form.save(commit=False)
            order_obj.seller = userplant_obj.user
            order_obj.buyer = self.request.user
        else:
            print(form.errors.as_data())
        order_obj.save()

        # validate and save OrderItem form
        if order_item_form.is_valid():
            order_item_obj = order_item_form.save(commit=False)
            order_item_obj.order = order_obj
            order_item_obj.user_plant = userplant_obj
            order_item_obj.save()
        else:
            print(order_item_form.errors.as_data())

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
    title = 'Purchase Order History'
    template_name = 'order/user_order_list.html'

    def get_queryset(self):
        # queryset = super().get_queryset()
        queryset = {
            'buyer_new': Order.objects.all().filter(
                buyer=self.request.user, status='CR'
            ),
            'buyer_in_progress': Order.objects.all().filter(
                buyer=self.request.user, status='IN'
            ),
            'buyer_completed': Order.objects.all().filter(
                buyer=self.request.user, status='FU'
            ),
            'buyer_canceled': Order.objects.all().filter(
                buyer=self.request.user, status='CA'
            ),
            'seller_new': Order.objects.all().filter(
                seller=self.request.user, status='CR'
            ),
            'seller_in_progress': Order.objects.all().filter(
                seller=self.request.user, status='IN'
            ),
            'seller_completed': Order.objects.all().filter(
                seller=self.request.user, status='FU'
            ),
            'seller_canceled': Order.objects.all().filter(
                seller=self.request.user, status='CA'
            ),
        }
        return queryset


class OrderDetailView(
    TemplateTitleMixin,
    ModelFormMixin,
    DetailView,
    LoginRequiredMixin,
):
    model = Order
    title = 'Order Detail'
    template_name = 'order/order_detail.html'
    form_class = SellerOrderForm

    def get_success_url(self):
        return reverse_lazy(
            'order:order_detail', kwargs={'pk': self.object.pk}
        )

    def get_context_data(self, *args, **kwargs):
        context = super(OrderDetailView, self).get_context_data(
            *args, **kwargs
        )
        # https://stackoverflow.com/questions/45659986/django-implementing-a-form-within-a-generic-detailview
        form = SellerOrderForm(instance=self.object)
        form.fields[
            'address_for_pickup'
        ].queryset = self.request.user.get_user_addresses.all()
        context['form'] = form

        order = context['object']
        context['total_num_items'] = order.get_total_num_items()
        return context

    def get_object(self, queryset=None):
        """Raise 404 error if User is not Order Buyer"""
        obj = super().get_object(queryset)
        if obj.buyer != self.request.user and obj.seller != self.request.user:
            raise Http404("Order number not found for signed-in user")
        return obj

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            print(form.errors.as_data())
            return self.form_invalid(form)

    def form_valid(self, form):
        obj = form.save()
        if obj.status == obj.OrderStatusOptions.IN_PROGRESS:
            obj.in_progress_date = timezone.now()
        if obj.status == obj.OrderStatusOptions.FULFILLED:
            obj.fulfilled_date = timezone.now()
        obj.save()
        return super(OrderDetailView, self).form_valid(form)


class BuyerOrderUpdateView(
    TemplateTitleMixin,
    UpdateView,
    LoginRequiredMixin,
):
    model = Order
    title = 'Update Order'
    form_class = OrderForm
    template_name = 'order/order_create.html'
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
        """Set form fields based on User and UserPlant attributes

        - Limits form address field to address's owned by user
        - Limits Handling field options to UserPlant handling options
        """
        form = super(BuyerOrderUpdateView, self).get_form(*args, **kwargs)
        form.fields[
            'address_for_shipping'
        ].queryset = self.request.user.get_user_addresses.all()

        # set Order form Handling field based on UserPlant handling options
        # Handling default includes both shipping and pickup options
        userplant_pk = self.object.get_order_items.all()[0].user_plant.pk
        userplant = get_object_or_404(UserPlant, pk=userplant_pk)
        if userplant.is_for_shipping and not userplant.is_for_pickup:
            form.fields['handling'].choices = [('SH', 'Shipping')]
        if not userplant.is_for_shipping and userplant.is_for_pickup:
            form.fields['handling'].choices = [('PI', 'Pickup')]
            form.fields['handling'].initial = 'PI'

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
            'order:order_detail', kwargs={'pk': self.object.pk}
        )


class OrderCancelView(LoginRequiredMixin, DeleteView):
    model = Order
    template_name = 'order/order_cancel.html'
    success_url = reverse_lazy('order:user_orders_all')

    def form_valid(self, form):
        """Set status to canceled

        - does not delete order from database
        - add quantity back to UserPlant
        """
        self.object.status = self.object.OrderStatusOptions.CANCELED
        self.object.canceled_date = timezone.now()
        self.object.canceled_by = self.request.user

        # add quantity back to Userplant quantity
        userplant_pk = self.object.get_order_items.all()[0].user_plant.pk
        userplant = get_object_or_404(UserPlant, pk=userplant_pk)
        curr_quantity_ordered = self.object.get_order_items.all()[0].quantity
        userplant.quantity += curr_quantity_ordered
        userplant.save()

        self.object.save()
        return redirect(self.success_url)

    def get_object(self, queryset=None):
        """Raise 404 error if User is not Order Buyer or Seller"""
        obj = super().get_object(queryset)
        if obj.buyer != self.request.user and obj.seller != self.request.user:
            raise Http404("Order number not found for signed-in user")
        return obj
