from django.contrib import admin
from .models import Thread, Post


#class PostAdmin(admin.ModelAdmin):
#    list_display = ['message', 'forum']

class ThreadAdmin(admin.ModelAdmin):
    list_display = ['title', 'link']
    
admin.site.register([Thread], ThreadAdmin)
admin.site.register([Post], admin.ModelAdmin)
