from django.contrib import admin
from .models import QuizEntry,TwitterLinkedAccount, FanCard
from django.utils.html import format_html


@admin.register(QuizEntry)
class QuizEntryAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'full_name', 'email', 'cpf', 'rg', 'created_at')
    list_filter = ('created_at', 'buy', 'attended_event')
    search_fields = ('full_name', 'email', 'cpf', 'rg')
    ordering = ('-created_at',)

@admin.register(TwitterLinkedAccount)
class TwitterLinkedAccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'twitter_username', 'twitter_id', 'created_at')
    search_fields = ('user__username', 'twitter_username', 'twitter_id')
    list_filter = ('created_at',)
    raw_id_fields = ('user',)

@admin.register(FanCard)
class FanCardAdmin(admin.ModelAdmin):
    list_display = ('user', 'photo_tag', 'created_at', 'updated_at')
    readonly_fields = ('photo_tag',)
    search_fields = ('user__username',)

    def photo_tag(self, obj):
        if obj.photo:
            return format_html('<img src="{}" style="max-height: 150px; max-width: 150px;" />', obj.photo.url)
        return "(Sem foto)"
    photo_tag.short_description = 'Foto da Carteirinha'    