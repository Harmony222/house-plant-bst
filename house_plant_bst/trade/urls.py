from django.urls import path
from .views import CreateThread, ListThreads

app_name = 'trade'

urlpatterns = [
    path('list-threads/', ListThreads.as_view(), name='list_threads'),
    path('list-threads/create-thread', CreateThread.as_view(),
         name='create-thread'),
    path('list-threads/create-thread', CreateThread.as_view(),
         name='create-thread')
]