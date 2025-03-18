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

def main():
    video_ids = ['dQw4w9WgXcQ', 'anotherVideoId']
    youtube_transcripts = {}

    for vid in video_ids:
        transcript = get_youtube_transcript(vid)
        if transcript:
            youtube_transcripts[vid] = transcript
            logger.info(f"Successfully fetched transcript for video ID: {vid}")
        else:
            logger.warning(f"Could not fetch transcript for video ID: {vid}")

    for vid, text in youtube_transcripts.items():
        logger.debug(f"Transcript for {vid}: {text[:100]}...")

if __name__ == '__main__':
    main()