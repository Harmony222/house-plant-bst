from django.contrib import admin
from .models import Plant, PlantCommonName, UserPlant

admin.site.register(Plant)
admin.site.register(PlantCommonName)
admin.site.register(UserPlant)
