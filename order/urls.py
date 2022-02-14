from django.urls import path

from order import views

app_name = 'order'

urlpatterns = [
    path('<int:pk>', views.order_plant, name='order_plant'),
]
