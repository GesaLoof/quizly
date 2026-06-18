from rest_framework.routers import DefaultRouter
from .views import QuizViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r'quizzes', QuizViewSet, basename='quiz')

urlpatterns = [
    path('', include(router.urls)),
]