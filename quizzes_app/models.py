from django.db import models
from django.conf import settings


class Video(models.Model):
    """
    Represents a video with a URL, title, and transcript.
    """
    url = models.URLField(unique=True)
    title = models.CharField(max_length=255)
    transcript = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Quiz(models.Model):
    """
    Represents a quiz associated with a video and a user, including its title, 
    description, and timestamps.
    """
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name="quizzes")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="quizzes"
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Question(models.Model):
    """
    Represents a question in a quiz, including its title, options, and the correct answer.
    """
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    question_title = models.CharField(max_length=500)
    question_options = models.JSONField()  # stores the list of options
    answer = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.question_title
