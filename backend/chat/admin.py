from django.contrib import admin
from .models import ChatHistory, Message

@admin.register(ChatHistory)
class ChatHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_message', 'bot_response', 'timestamp') 
    search_fields = ('user_message', 'bot_response')  
    list_filter = ('timestamp',)  
    ordering = ('-timestamp',)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'chat', 'role', 'content', 'timestamp')
    search_fields = ('content', 'role')
    list_filter = ('timestamp', 'role')
    ordering = ('-timestamp',)