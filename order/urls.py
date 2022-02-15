from django.urls import path

from order import views

app_name = 'order'

urlpatterns = [
    # path('create/<int:pk>/', views.order_plant, name='order_plant'),
    path(
        'create/<int:userplant_pk>/',
        views.OrderCreateView.as_view(),
        name='order_plant',
    ),
]
