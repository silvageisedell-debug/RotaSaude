from django.contrib import admin
from .models import Veiculo, Modelo, Marca

admin.site.register(Veiculo)
admin.site.register(Modelo)
admin.site.register(Marca)