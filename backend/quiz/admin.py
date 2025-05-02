from django.contrib import admin
from .models import QuizEntry,TwitterLinkedAccount

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