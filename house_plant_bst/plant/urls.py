from django.urls import path

from plant import views

app_name = "plant"

urlpatterns = [
    path('', views.PlantListView.as_view(), name='all_plants'),
    path('<int:pk>/', views.PlantDetailView.as_view(), name='plant_detail'),
    path('create/', views.PlantCreateView.as_view(), name='plant_create'),
    path(
        '<int:pk>/update/',
        views.PlantUpdateView.as_view(),
        name='plant_update',
    ),
    path(
        '<int:pk>/delete/',
        views.PlantDeleteView.as_view(),
        name='plant_delete',
    ),
]
