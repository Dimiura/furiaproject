from django.contrib import admin
from .models import QuizEntry

@admin.register(QuizEntry)
class QuizEntryAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'full_name', 'email', 'cpf', 'rg', 'created_at')
    list_filter = ('created_at', 'buy', 'attended_event')
    search_fields = ('full_name', 'email', 'cpf', 'rg')
    ordering = ('-created_at',)