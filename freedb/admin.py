from django.contrib import admin
from .models import Database, Collection

class DatabaseAdminView(admin.ModelAdmin):
    list_display = ['name', 'owner']


class CollectionAdminView(admin.ModelAdmin):
    list_display = ['id', 'name', 'database']


admin.site.register(Database, DatabaseAdminView)
admin.site.register(Collection, CollectionAdminView)
# admin.site.register(Album, AlbumAdminView)
# # admin.site.register(ImageFile)
# admin.site.register(Image, ImageAdminView)
# admin.site.register(Tag)
