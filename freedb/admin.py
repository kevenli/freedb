from django.contrib import admin
from .models import Database, Collection, Field

class DatabaseAdminView(admin.ModelAdmin):
    list_display = ['name', 'owner']


class CollectionAdminView(admin.ModelAdmin):
    list_display = ['id', 'name', 'database']


class FieldAdminView(admin.ModelAdmin):
    list_display = ['id', 'field_name', 'field_type', 'sort_no']


admin.site.register(Database, DatabaseAdminView)
admin.site.register(Collection, CollectionAdminView)
admin.site.register(Field, FieldAdminView)
# admin.site.register(Album, AlbumAdminView)
# # admin.site.register(ImageFile)
# admin.site.register(Image, ImageAdminView)
# admin.site.register(Tag)
