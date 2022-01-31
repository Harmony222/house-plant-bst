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
                               related_name='get_seller_trades')
    buyer = models.ForeignKey(User,
                              null=True,
                              verbose_name='Buyer',
                              on_delete=models.SET_NULL,
                              related_name='get_buyer_trades')
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


class Thread(models.Model):
    """Each Thread instance object ties a User's thread to a Trade object"""
    user = models.ForeignKey(User,
                             null=True,
                             verbose_name='Thread User',
                             on_delete=models.SET_NULL,
                             related_name='get_user_threads')
    recipient = models.ForeignKey(User,
                                  null=True,
                                  verbose_name='Thread Recipient',
                                  on_delete=models.SET_NULL,
                                  related_name='get_recipient_threads')
    trade = models.ForeignKey(Trade,
                              verbose_name='Trade',
                              on_delete=models.CASCADE,
                              related_name='get_trade_threads')
    has_unread = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'Threads'

    def __str__(self):
        return f'trade id: {self.trade.id}, \
               thread id: {self.id}, \
               user: {self.user.username}, \
               recipientL {self.recipient.username}'


class Message(models.Model):
    """Each Message instance object ties a User's message to a Thread object"""
    sender = models.ForeignKey(User,
                               null=True,
                               verbose_name='Message Sender',
                               on_delete=models.SET_NULL,
                               related_name='get_sent_messages')
    recipient = models.ForeignKey(User,
                                  null=True,
                                  verbose_name='Message Recipient',
                                  on_delete=models.SET_NULL,
                                  related_name='get_received_messages')
    thread = models.ForeignKey(Thread,
                               verbose_name='Thread',
                               on_delete=models.CASCADE,
                               related_name='get_thread_messages')
    message = models.TextField()
    message_sent_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Messages'

    def __str__(self):
        return f'thread id: {self.thread.id}, \
               message id: {self.id}, \
               sender: {self.sender.username}, \
               recipient: {self.recipient.username}'


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
