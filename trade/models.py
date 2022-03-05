from django.db import models
from plant.models import UserPlant
from order.models import Address
from django.conf import settings
User = settings.AUTH_USER_MODEL


class Trade(models.Model):
    # Trade Status Constants
    SENT = 'SE'
    ACCEPTED = 'AC'
    REJECTED = 'RE'
    UNAVAILABLE = 'UN'

    TRADE_STATUS_CHOICES = [
        (SENT, 'Sent'),
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected'),
        (UNAVAILABLE, 'Unavailable')
    ]

    # Accepted Handling Method Constants
    UNDEFINED = 'UN'
    SHIP = 'SH'
    PICKUP = 'PI'

    ACCEPTED_HANDLING_METHOD = [
        (UNDEFINED, 'Undefined'),
        (SHIP, 'Shipping'),
        (PICKUP, 'Pickup')
    ]

    seller = models.ForeignKey(
        User,
        null=True,
        verbose_name='Seller',
        on_delete=models.SET_NULL,
        related_name='get_seller_trades'
    )
    buyer = models.ForeignKey(
        User,
        null=True,
        verbose_name='Buyer',
        on_delete=models.SET_NULL,
        related_name='get_buyer_trades'
    )
    request_date = models.DateTimeField(auto_now_add=True)
    response_date = models.DateTimeField(null=True, blank=True)
    trade_status = models.CharField(
        max_length=2,
        choices=TRADE_STATUS_CHOICES,
        default=SENT
    )
    accepted_handling_method = models.CharField(
        max_length=2,
        choices=ACCEPTED_HANDLING_METHOD,
        default=UNDEFINED
    )
    is_offered_for_pickup = models.BooleanField(default=False)
    is_offered_for_shipping = models.BooleanField(default=False)
    requester_address = models.ForeignKey(
        Address,
        null=True,
        verbose_name='Requester\'s Address',
        on_delete=models.SET_NULL,
        related_name='get_trade_requester_address'
    )
    seller_address = models.ForeignKey(
        Address,
        null=True,
        blank=True,
        verbose_name='Seller\'s Address',
        on_delete=models.SET_NULL,
        related_name='get_trade_seller_address'
    )


    class Meta:
        verbose_name_plural = 'Trades'

    def __str__(self):
        """String for representing the Trade object (ex: the Admin site)."""
        seller_username = "Deleted User" if self.seller is None else\
            self.seller.username
        buyer_username = "Deleted User" if self.buyer is None else\
            self.buyer.username
        return f'trade id: {self.id}, \
               buyer: {buyer_username}, \
               seller: {seller_username} '


class Message(models.Model):
    """Each Message instance object ties a User's message to a Thread object"""
    sender = models.ForeignKey(
        User,
        null=True,
        verbose_name='Message Sender',
        on_delete=models.SET_NULL,
        related_name='get_sent_messages'
    )
    recipient = models.ForeignKey(
        User,
        null=True,
        verbose_name='Message Recipient',
        on_delete=models.SET_NULL,
        related_name='get_received_messages'
    )
    trade = models.ForeignKey(
        Trade,
        verbose_name='Trade',
        on_delete=models.CASCADE,
        related_name='get_trade_messages'
    )
    message = models.TextField()
    message_sent_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Messages'

    def __str__(self):
        sender_username = "Deleted User" if self.sender is None else\
            self.sender.username
        recipient_username = "Deleted User" if self.recipient is None else\
            self.recipient.username

        return f'trade id: {self.trade.pk}, \
               message id: {self.id}, \
               sender: {sender_username}, \
               recipient: {recipient_username}'


class TradeItem(models.Model):
    """Each TradeItem instance object indicates a relationship between a Trade
    object and a UserPlant object."""
    trade = models.ForeignKey(
        Trade,
        verbose_name='Trade',
        on_delete=models.CASCADE,
        related_name='get_trade_items'
    )
    user_plant = models.ForeignKey(
        UserPlant,
        verbose_name='User Plant',
        on_delete=models.RESTRICT,
        related_name='get_trade_items'
    )
    quantity = models.PositiveSmallIntegerField(default=1)
    chosen_flag = models.BooleanField(
        default=None,
        blank=True,
        null=True
    )

    class Meta:
        verbose_name_plural = 'Trade Items'

    def __str__(self):
        owner_username = "Deleted User" if self.user_plant.user is None else\
                         self.user_plant.user.username
        return f'trade id: {self.trade.id}, item id: {self.id} \
               owner: {owner_username}, \
               plant: {self.user_plant.plant.scientific_name}'
