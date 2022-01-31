from django.contrib import admin
from .models import Message, Thread, Trade, TradeItem

admin.site.register(Message)
admin.site.register(Thread)
admin.site.register(Trade)
admin.site.register(TradeItem)
