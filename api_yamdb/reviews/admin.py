from django.contrib import admin
from reviews.models import Category, Comment, Genre, Review, Title


class GenresInline(admin.TabularInline):
    model = Title.genre.through


class TitleAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'category', 'year', 'description')
    inlines = [
        GenresInline
    ]
    exclude = ('genre',)


class CommentAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'pub_date', 'review', 'author')


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'text', 'pub_date', 'author', 'score')


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug')


class GenreAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug')
    inlines = [
        GenresInline
    ]


admin.site.register(Title, TitleAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Genre, GenreAdmin)
