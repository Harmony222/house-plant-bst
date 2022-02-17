from django.db import models
from plant.models import UserPlant
from django.conf import settings
from django.urls import reverse_lazy

User = settings.AUTH_USER_MODEL


class Address(models.Model):
    """Each Address instance object ties a ship-to address to an Order
    object"""

    street = models.CharField(max_length=150)
    city = models.CharField(max_length=150)
    state = models.CharField(max_length=2)
    zip = models.CharField(max_length=10)
    user = models.ForeignKey(
        User,
        null=True,
        verbose_name='User',
        on_delete=models.SET_NULL,
        related_name='get_user_addresses',
    )

    class Meta:
        verbose_name_plural = 'Addresses'

    def __str__(self):
        return f'{self.street} \n\
               {self.city}, \
               {self.state} \
               {self.zip}'


class Order(models.Model):
    address = models.ForeignKey(
        Address,
        null=True,
        verbose_name='Ship to address',
        on_delete=models.RESTRICT,
        related_name='get_order_address',
    )
    seller = models.ForeignKey(
        User,
        null=True,
        verbose_name='Seller',
        on_delete=models.SET_NULL,
        related_name='get_seller_orders',
    )
    buyer = models.ForeignKey(
        User,
        null=True,
        verbose_name='Buyer',
        on_delete=models.SET_NULL,
        related_name='get_buyer_orders',
    )
    creation_date = models.DateTimeField(auto_now_add=True)
    in_progress_date = models.DateTimeField(null=True, blank=True)
    fulfilled_date = models.DateTimeField(null=True, blank=True)
    total_price = models.DecimalField(
        max_digits=6, decimal_places=2, default=0.00
    )

    class Meta:
        verbose_name_plural = 'Orders'

    def __str__(self):
        """String for representing the Order object (ex: the Admin site)."""
        seller_username = (
            "Deleted User" if self.seller is None else self.seller.username
        )
        buyer_username = (
            "Deleted User" if self.buyer is None else self.buyer.username
        )
        return f'order id: {self.id}, \
               buyer: {buyer_username}, \
               seller: {seller_username} '

    def get_total_num_items(self):
        count = 0
        for item in self.get_order_items.all():
            count += item.quantity
        return count

    def calculate_total_price(self):
        total_price = 0.0
        for item in self.get_order_items.all():
            total_price += float(item.user_plant.unit_price * item.quantity)
        return total_price

    def get_buyer_update_url(self):
        """Return the url for buyer to update order"""
        return reverse_lazy('order:buyer_order_update', kwargs={'pk': self.pk})


class OrderItem(models.Model):
    """Each OrderItem instance object indicates a relationship between an Order
    object and a UserPlant object."""

    order = models.ForeignKey(
        Order,
        verbose_name='Order',
        on_delete=models.CASCADE,
        related_name='get_order_items',
    )
    user_plant = models.ForeignKey(
        UserPlant,
        verbose_name='User Plant',
        on_delete=models.RESTRICT,
        related_name='get_order_items',
    )
    quantity = models.PositiveSmallIntegerField(default=1)

    class Meta:
        verbose_name_plural = 'Order Items'

    def __str__(self):
        username = (
            "Deleted User"
            if self.user_plant.user is None
            else self.user_plant.user
        )
        return f'order id: {self.order.id}, item id: {self.id} \
               owner: {username}, \
               plant: {self.user_plant.plant.scientific_name}'
