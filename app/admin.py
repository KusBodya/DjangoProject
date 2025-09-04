from django.contrib import admin
from .models import Source, Quote, Vote

@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)

@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ("id", "source", "text")
    list_filter = ("source",)
    search_fields = ("text",)

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ("id", "quote", "user", "value", "created_at")
    list_filter = ("value",)
