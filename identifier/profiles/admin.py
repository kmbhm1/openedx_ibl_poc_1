from django.contrib import admin
from .models import Greeting


class GreetingAdmin(admin.ModelAdmin):
    pass


admin.site.register(Greeting, GreetingAdmin)