from django.contrib import admin
from .models import Message, Trade, TradeItem

admin.site.register(Message)
admin.site.register(Trade)
admin.site.register(TradeItem)
