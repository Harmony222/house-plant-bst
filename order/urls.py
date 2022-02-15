from django.urls import path

from order import views

app_name = 'order'

urlpatterns = [
    path(
        'create/<int:userplant_pk>/',
        views.OrderCreateView.as_view(),
        name='order_plant',
    ),
    path(
        'address/create/',
        views.AddressCreateView.as_view(),
        name='address_create',
    ),
    path('', views.UserOrderListView.as_view(), name='user_orders_all'),
]
