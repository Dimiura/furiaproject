from rest_framework import generics, permissions
from .models import QuizEntry
from .serializers import QuizEntrySerializer

class QuizEntryCreateView(generics.CreateAPIView):
    queryset = QuizEntry.objects.all()
    serializer_class = QuizEntrySerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
