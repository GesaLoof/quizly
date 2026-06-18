import os
import tempfile
import yt_dlp
import whisper
import json
from django.conf import settings
from google import genai


def get_transcript(url):
    model = whisper.load_model("base")

    with tempfile.TemporaryDirectory() as tmpdir:
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": os.path.join(tmpdir, "audio.%(ext)s"),
            "quiet": True,
            "noplaylist": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get("title", "Unknown Title")
            audio_file = ydl.prepare_filename(info)

        result = model.transcribe(audio_file)
        transcript = result["text"]

    return title, transcript


def generate_quiz(transcript):
    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    prompt = f"""Based on the following transcript, generate a quiz in valid JSON format.

    The quiz must follow this exact structure:
    {{
    "title": "Create a concise quiz title based on the topic of the transcript.",
    "description": "Summarize the transcript in no more than 150 characters. Do not include any quiz questions or answers.",
    "questions": [
        {{
        "question_title": "The question goes here.",
        "question_options": ["Option A", "Option B", "Option C", "Option D"],
        "answer": "The correct answer from the above options"
        }},
        ...
        (exactly 10 questions)
    ]
    }}
    Requirements:
    - Each question must have exactly 4 distinct answer options.
    - Only one correct answer is allowed per question, and it must be present in 'question_options'.
    - The output must be valid JSON and parsable as-is (e.g., using Python's json.loads).
    - Do not include explanations, comments, or any text outside the JSON.
    Transcript: {transcript}"""
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite", contents=prompt
    )

    text = (
        response.text.strip()
        .removeprefix("```json")
        .removeprefix("```")
        .removesuffix("```")
        .strip()
    )
    data = json.loads(text)
    return data
