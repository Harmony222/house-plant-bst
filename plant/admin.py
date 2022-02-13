from django.contrib import admin
from .models import Plant, PlantCommonName, UserPlant, Tag


class PlantAdmin(admin.ModelAdmin):
    readonly_fields = ('pk',)


admin.site.register(Plant, PlantAdmin)
admin.site.register(PlantCommonName)
admin.site.register(UserPlant)
admin.site.register(Tag)
