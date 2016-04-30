from django.contrib import admin
from .models import Thread, Post


class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'forum', 'message']


class ThreadAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'link', 'forum']

admin.site.register([Thread], ThreadAdmin)
admin.site.register([Post], PostAdmin)
