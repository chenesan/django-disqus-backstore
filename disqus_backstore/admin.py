from django.contrib import admin
from .models import Thread, Post

admin.site.register([Thread], admin.ModelAdmin)
admin.site.register([Post], admin.ModelAdmin)
