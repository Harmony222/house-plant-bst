from django.urls import include, path
from .views import CreateTrade, OrderHistory, TradeView, CreateMessage, \
      TradeResponse

app_name = 'trade'

urlpatterns = [
    path('order_history/',
         OrderHistory.as_view(),
         name='order_history'),
    path('order_history/<int:pk>/',
         TradeView.as_view(),
         name='trade'),
    path('order_history/<int:pk>/create_message/',
         CreateMessage.as_view(),
         name='create_message'),
    path('order_history/<int:pk>/trade_response/',
         TradeResponse.as_view(),
         name='trade_response'),
    # test
    path('order_history/create_trade/',
         CreateTrade.as_view(),
         name='create_trade'),
    path('order_history/<int:pk>/create_trade/',
         CreateTrade.as_view(),
         name='create_trade_submit'),
]
