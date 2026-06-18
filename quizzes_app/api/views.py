from rest_framework.response import Response
from rest_framework import status, mixins, viewsets
from rest_framework.permissions import IsAuthenticated
from quizzes_app.models import Video, Quiz, Question
from quizzes_app.services import get_transcript, generate_quiz
from google.api_core.exceptions import ResourceExhausted
from .serializers import QuizListSerializer, QuizSerializer
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied


class QuizViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """
    Provides CRUD operations for quizzes, including listing, creating, retrieving, 
    updating, and deleting quizzes. Ensures that users can only access their own quizzes.
    """
    permission_classes = [IsAuthenticated]
    queryset = Quiz.objects.all()

    def get_serializer_class(self):
        if self.action in ["list", "retrieve", "update", "partial_update"]:
            return QuizListSerializer
        return QuizSerializer

    def get_queryset(self):
        if self.action == "list":
            return Quiz.objects.filter(user=self.request.user)
        return Quiz.objects.all()

    def get_object(self):
        quiz = get_object_or_404(Quiz, pk=self.kwargs["pk"])
        if quiz.user != self.request.user:
            raise PermissionDenied("You do not have permission to access this quiz.")
        return quiz

    def create(self, request, *args, **kwargs):
        url = request.data.get("url")
        if not url:
            return Response(
                {"detail": "URL is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        video, created = Video.objects.get_or_create(
            url=url, defaults={"title": "", "transcript": ""}
        )

        if created:
            title, transcript = get_transcript(url)
            video.title = title
            video.transcript = transcript
            video.save()

        existing_quiz = Quiz.objects.filter(user=request.user, video=video).first()
        if existing_quiz:
            return Response(
                QuizSerializer(existing_quiz).data, status=status.HTTP_200_OK
            )

        try:
            quiz_data = generate_quiz(video.transcript)
        except ResourceExhausted:
            return Response(
                {"detail": "AI service quota exceeded, please try again later."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        quiz = Quiz.objects.create(
            user=request.user,
            video=video,
            title=quiz_data["title"],
            description=quiz_data["description"],
        )

        for q in quiz_data["questions"]:
            Question.objects.create(
                quiz=quiz,
                question_title=q["question_title"],
                question_options=q["question_options"],
                answer=q["answer"],
            )

        return Response(QuizSerializer(quiz).data, status=status.HTTP_201_CREATED)
