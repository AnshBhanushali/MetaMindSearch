import logging
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, VideoUnavailable, NoTranscriptFound

# Configure logging for detailed output in production
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def get_youtube_transcript(video_id, languages=['en']):
    """
    Fetches the transcript for a given YouTube video ID.
    """
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=languages)
        transcript_text = " ".join(segment['text'] for segment in transcript_list)
        return transcript_text
    except (TranscriptsDisabled, VideoUnavailable, NoTranscriptFound) as e:
        logger.error(f"Transcript not available for video {video_id}: {e}")
    except Exception as e:
        logger.error(f"Error fetching transcript for video {video_id}: {e}")
    return None