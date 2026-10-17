from elevenlabs.client import ElevenLabs
import os

class VoiceService:
    def __init__(self):
        self.client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
        self.voice_id = os.getenv("ELEVENLABS_VOICE_ID")

    def generate_audio(self, text, output_filename="speech.mp3"):
        audio = self.client.generate(text=text, voice=self.voice_id)
        with open(output_filename, "wb") as f:
            for chunk in audio:
                f.write(chunk)
        return output_filename
