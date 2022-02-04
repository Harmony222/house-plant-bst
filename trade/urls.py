from django.urls import path
from .views import CreateTrade, ListTrades, TradeView, CreateMessage, \
      TradeResponse

app_name = 'trade'

urlpatterns = [
    path('list_trades/',
         ListTrades.as_view(),
         name='list_trades'),
    path('list_trades/create_trade/',
         CreateTrade.as_view(),
         name='create_trade'),
    path('list_trades/<int:pk>/',
         TradeView.as_view(),
         name='trade'),
    path('list_trades/<int:pk>/create_message/',
         CreateMessage.as_view(),
         name='create_message'),
    path('list_trades/<int:pk>/trade_response/',
         TradeResponse.as_view(),
         name='trade_response')
]
