from rest_framework import serializers
from quizzes_app.models import Quiz, Question, Video


class QuestionListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing questions with limited fields (excludes timestamps).
    """
    class Meta:
        model = Question
        fields = [
            "id",
            "question_title",
            "question_options",
            "answer",
        ]  # no created_at/updated_at


class QuestionSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed question data, including timestamps.
    """
    class Meta:
        model = Question
        fields = [
            "id",
            "question_title",
            "question_options",
            "answer",
            "created_at",
            "updated_at",
        ]


class QuizListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing quizzes with related questions and video URL.
    Includes validation to restrict unexpected fields.
    """
    questions = QuestionListSerializer(many=True, read_only=True)
    video_url = serializers.CharField(source="video.url", read_only=True)

    class Meta:
        model = Quiz
        fields = [
            "id",
            "title",
            "description",
            "created_at",
            "updated_at",
            "video_url",
            "questions",
        ]

    def validate(self, attrs):
        allowed_fields = set(self.fields.keys()) - {
            "questions",
            "video_url",
            "id",
            "created_at",
            "updated_at",
        }
        incoming_fields = set(self.initial_data.keys())
        unexpected_fields = incoming_fields - allowed_fields

        if unexpected_fields:
            raise serializers.ValidationError(
                {field: "This field is not allowed." for field in unexpected_fields}
            )
        return attrs


class QuizSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed quiz data, including related questions and video URL.
    """
    questions = QuestionSerializer(many=True, read_only=True)
    video_url = serializers.CharField(source="video.url", read_only=True)

    class Meta:
        model = Quiz
        fields = [
            "id",
            "title",
            "description",
            "created_at",
            "updated_at",
            "video_url",
            "questions",
        ]
