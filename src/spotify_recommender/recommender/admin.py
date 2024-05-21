from django.contrib import admin
from .models import Genre, Token, Track, User, Rating

# Register your models here.


class GenreAdmin(admin.ModelAdmin):
    list_display = ["id", "genre"]


class TokenAdmin(admin.ModelAdmin):
    list_display = ["id", "userid", "expira_la", "access_token"]


class TrackAdmin(admin.ModelAdmin):
    list_display = ["id", "spotifyid", "releasedate", "artists", "explicit"]


class UserAdmin(admin.ModelAdmin):
    list_display = ["id", "spotifyid"]


class RatingAdmin(admin.ModelAdmin):
    list_display = ["userid", "songid", "rating"]


admin.site.register(Genre, GenreAdmin)
admin.site.register(Token, TokenAdmin)
admin.site.register(Track, TrackAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Rating, RatingAdmin)
