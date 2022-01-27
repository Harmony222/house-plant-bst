from django.db import models
from plant.models import UserPlant
from django.conf import settings
User = settings.AUTH_USER_MODEL


class Trade(models.Model):
    # Trade Status Constants
    SENT = 'SE'
    ACCEPTED = 'AC'
    REJECTED = 'RJ'

    TRADE_STATUS_CHOICES = [
        (SENT, 'sent'),
        (ACCEPTED, 'accepted'),
        (REJECTED, 'rejected'),
    ]

    seller = models.ForeignKey(User,
                               null=True,
                               verbose_name='Seller',
                               on_delete=models.SET_NULL,
                               related_name='getSellerTrades')
    buyer = models.ForeignKey(User,
                              null=True,
                              verbose_name='Buyer',
                              on_delete=models.SET_NULL,
                              related_name='getBuyerTrades')
    request_date = models.DateTimeField(auto_now_add=True)
    response_date = models.DateTimeField(null=True, blank=True)
    trade_status = models.CharField(max_length=2,
                                    choices=TRADE_STATUS_CHOICES,
                                    default=SENT)

    class Meta:
        verbose_name_plural = 'Trades'

    def __str__(self):
        """String for representing the Trade object (ex: the Admin site)."""
        return f'trade id: {self.id}, \
               buyer: {self.buyer.username}, \
               seller: {self.seller.username} '


class Message(models.Model):
    """Each Message instance object ties a User's message to a Trade object"""
    sender = models.ForeignKey(User,
                               null=True,
                               verbose_name='Message Sender',
                               on_delete=models.SET_NULL,
                               related_name='get_user_messages')
    trade = models.ForeignKey(Trade,
                              verbose_name='Trade',
                              on_delete=models.CASCADE,
                              related_name='get_trade_messages')
    message = models.TextField()
    message_sent_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Messages'

    def __str__(self):
        return f'trade id: {self.trade.id}, \
               message id: {self.id}, \
               sender: {self.sender.username}'


class TradeItem(models.Model):
    """Each TradeItem instance object indicates a relationship between a Trade
    object and a UserPlant object."""
    trade = models.ForeignKey(Trade,
                              verbose_name='Trade',
                              on_delete=models.CASCADE,
                              related_name='get_trade_items')
    user_plant = models.ForeignKey(UserPlant,
                                   verbose_name='User Plant',
                                   on_delete=models.RESTRICT,
                                   related_name='get_trade_items')
    quantity = models.PositiveSmallIntegerField(default=1)

    class Meta:
        verbose_name_plural = 'Trade Items'

    def __str__(self):
        return f'trade id: {self.trade.id}, item id: {self.id} \
               owner: {self.user_plant.user.username}, \
               plant: {self.user_plant.plant.scientific_name}'
