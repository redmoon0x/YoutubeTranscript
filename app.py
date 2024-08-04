from flask import Flask, render_template, request
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import NoTranscriptFound, TranscriptsDisabled
import re

app = Flask(__name__)

def extract_video_id(url):
    """
    Extracts the video ID from a YouTube URL.
    """
    video_id_match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', url)
    return video_id_match.group(1) if video_id_match else None

@app.route('/', methods=['GET', 'POST'])
def index():
    transcript_text = None
    if request.method == 'POST':
        url = request.form.get('video_url')
        video_id = extract_video_id(url)
        if video_id:
            try:
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                try:
                    # Try to find a manually created transcript
                    transcript = transcript_list.find_manually_created_transcript(['en'])
                    transcript_data = transcript.fetch()
                    transcript_text = ' '.join([item['text'] for item in transcript_data])
                except NoTranscriptFound:
                    # If no manually created transcript is found, use the automatically generated one
                    try:
                        transcript = transcript_list.find_generated_transcript(['en'])
                        transcript_data = transcript.fetch()
                        transcript_text = ' '.join([item['text'] for item in transcript_data])
                        transcript_text = f"(Auto-generated) {transcript_text}"
                    except NoTranscriptFound:
                        transcript_text = "No transcript available for this video."
            except TranscriptsDisabled:
                transcript_text = "Transcription not available as subtitles are disabled for this video."
            except Exception as e:
                transcript_text = f"Error: {e}"
        else:
            transcript_text = "Invalid YouTube URL"
    return render_template('index.html', transcript=transcript_text)

@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
