from django.shortcuts import render

# from django.views.generic import (
#     TemplateView,
# )


def order_plant(request, pk):
    context = {'pk': pk}
    return render(request, 'order/order_plant.html', context)
