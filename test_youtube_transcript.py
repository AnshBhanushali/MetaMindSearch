import pytest
import logging

# Import exceptions from the API package
from youtube_transcript_api._errors import TranscriptsDisabled, VideoUnavailable, NoTranscriptFound

# Import the function to test. Adjust the module name if needed.
from youtubeScraper import get_youtube_transcript

# A sample transcript list to simulate a successful API response
sample_transcript = [
    {'text': 'Hello'},
    {'text': 'World'},
]

def fake_get_transcript_success(video_id, languages):
    """Fake get_transcript function that simulates a successful API call."""
    return sample_transcript

def fake_get_transcript_transcripts_disabled(video_id, languages):
    """Fake get_transcript function that simulates a TranscriptsDisabled error."""
    raise TranscriptsDisabled("Transcripts are disabled for this video.")

def fake_get_transcript_video_unavailable(video_id, languages):
    """Fake get_transcript function that simulates a VideoUnavailable error."""
    raise VideoUnavailable("Video is unavailable.")

def fake_get_transcript_no_transcript_found(video_id, languages):
    """Fake get_transcript function that simulates a NoTranscriptFound error.
       Now supplies all required keyword arguments: video_id, requested_language_codes, and transcript_data."""
    raise NoTranscriptFound(video_id=video_id, requested_language_codes=languages, transcript_data=[])




def fake_get_transcript_generic_error(video_id, languages):
    """Fake get_transcript function that simulates a generic error."""
    raise Exception("Some generic error")

def test_get_youtube_transcript_success(monkeypatch, caplog):
    # Override the get_transcript function with our fake success version
    monkeypatch.setattr("youtube_transcript_api.YouTubeTranscriptApi.get_transcript", fake_get_transcript_success)
    
    transcript = get_youtube_transcript("dummy_video_id")
    assert transcript == "Hello World", "Transcript should be the joined text from the sample list."

def test_get_youtube_transcript_transcripts_disabled(monkeypatch, caplog):
    monkeypatch.setattr("youtube_transcript_api.YouTubeTranscriptApi.get_transcript", fake_get_transcript_transcripts_disabled)
    
    transcript = get_youtube_transcript("dummy_video_id")
    assert transcript is None, "Transcript should be None when transcripts are disabled."
    assert "Transcript not available" in caplog.text

def test_get_youtube_transcript_video_unavailable(monkeypatch, caplog):
    monkeypatch.setattr("youtube_transcript_api.YouTubeTranscriptApi.get_transcript", fake_get_transcript_video_unavailable)
    
    transcript = get_youtube_transcript("dummy_video_id")
    assert transcript is None, "Transcript should be None when video is unavailable."
    assert "Transcript not available" in caplog.text

def test_get_youtube_transcript_no_transcript_found(monkeypatch, caplog):
    monkeypatch.setattr("youtube_transcript_api.YouTubeTranscriptApi.get_transcript", fake_get_transcript_no_transcript_found)
    
    transcript = get_youtube_transcript("dummy_video_id")
    assert transcript is None, "Transcript should be None when no transcript is found."
    assert "Transcript not available" in caplog.text

def test_get_youtube_transcript_generic_error(monkeypatch, caplog):
    monkeypatch.setattr("youtube_transcript_api.YouTubeTranscriptApi.get_transcript", fake_get_transcript_generic_error)
    
    transcript = get_youtube_transcript("dummy_video_id")
    assert transcript is None, "Transcript should be None when a generic error occurs."
    assert "Error fetching transcript" in caplog.text
