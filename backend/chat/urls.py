from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import ChatBotView, ChatHistoryDetailView, RecentChatHistoryView, NewChatView, message_count

urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', ChatBotView.as_view(), name='chat'),
    path('chat-history/<int:pk>/', ChatHistoryDetailView.as_view(), name='chat-history-detail'),
    path('recent-chats/', RecentChatHistoryView.as_view(), name='recent-chats'),
    path('new-chat/', NewChatView.as_view(), name='new-chat'),
    path('history-count/', message_count, name='chat-history-count'),
]