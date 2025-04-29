from django.urls import path, include
from django.contrib import admin


urlpatterns = [
    path('admin/', admin.site.urls),
    path('chat/', include('chat.urls')),
    path('auth/', include('authentication.urls')),
    path('api/v1/quiz/', include('quiz.urls')),
]