from django.contrib import admin
from .models import Distance
# Register your models here.
class SensorAdmin(admin.ModelAdmin):
    list_display = ('distance','pub_date',)

admin.site.register(Distance, SensorAdmin)
