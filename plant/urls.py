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

# UserPlant paths for Marketplace
urlpatterns.extend(
    [
        path(
            'marketplace/',
            views.MarketplacePlantListView.as_view(),
            name='marketplace_plants',
        ),
        path(
            'marketplace/<int:pk>/',
            views.MarketplacePlantDetailView.as_view(),
            name='marketplace_plant_detail',
        ),
    ]
)
# UserPlant paths for Signed in User
urlpatterns.extend(
    [
        path(
            'userplant/',
            views.UserPlantListView.as_view(),
            name='userplant_all',
        ),
        path(
            'userplant/<int:pk>/',
            views.UserPlantDetailView.as_view(),
            name='userplant_detail',
        ),
        path(
            'userplant/create/',
            views.UserPlantCreateView.as_view(),
            name='userplant_create',
        ),
        path(
            'userplant/<int:pk>/update/',
            views.UserPlantUpdateView.as_view(),
            name='userplant_update',
        ),
    ]
)
