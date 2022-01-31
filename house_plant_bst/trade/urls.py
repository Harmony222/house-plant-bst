from django.urls import path
from .views import CreateThread, ListThreads, ThreadView, CreateMessage

app_name = 'trade'

urlpatterns = [
    path('list-threads/',
         ListThreads.as_view(),
         name='list-threads'),
    path('list-threads/create-thread/',
         CreateThread.as_view(),
         name='create-thread'),
    path('list-threads/<int:pk>/',
         ThreadView.as_view(),
         name='thread'),
    path('list-threads/<int:pk>/create-message/',
         CreateMessage.as_view(),
         name='create-message')
]