from elevenlabs.client import AsyncElevenLabs

from app.clients.elevenlabs.patched_elevenlabs import AsyncRealtimeTextToSpeechClient


class PatchedAsyncElevenLabs(AsyncElevenLabs):
    """
    A patched version of the AsyncElevenLabs client that includes our custom
    realtime text-to-speech client.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.realtime_text_to_speech = AsyncRealtimeTextToSpeechClient(
            client_wrapper=self._client_wrapper
        )
