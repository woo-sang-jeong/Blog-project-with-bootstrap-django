from django.contrib import admin
from .models import Post, Category, Tag
from django_summernote.admin import SummernoteModelAdmin

# Register your models here.

#admin.site.register(Post)


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name', )}

# summernote 적용
class SummerAdmin(SummernoteModelAdmin):
    summernote_fileds = 'content'


admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Post, SummerAdmin)
