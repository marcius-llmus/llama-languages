from typing import AsyncGenerator, Optional

from elevenlabs import VoiceSettings

from app.clients.elevenlabs.patched_elevenlabs import AsyncRealtimeTextToSpeechClient


class ElevenLabsTTS:
    def __init__(
        self,
        realtime_client: AsyncRealtimeTextToSpeechClient,
        voice_id: str,
        *,
        model_id: str = "eleven_flash_v2_5",
        stability: Optional[float] = 0.5,
        similarity_boost: Optional[float] = 0.8,
        style: Optional[float] = 0.0,
        use_speaker_boost: bool = False,
        output_format: str = "pcm_24000",
    ):
        self.realtime_client = realtime_client
        self.voice_id = voice_id
        self.voice_settings = VoiceSettings(
            stability=stability,
            similarity_boost=similarity_boost,
            style=style,
            use_speaker_boost=use_speaker_boost,
        )
        self.model_id = model_id
        self.output_format = output_format

    async def stream(
        self, text: AsyncGenerator[str, None]
    ) -> AsyncGenerator[bytes, None]:
        audio_stream = self.realtime_client.convert_realtime(
            text=text,
            voice_id=self.voice_id,
            voice_settings=self.voice_settings,
            model_id=self.model_id,
            output_format=self.output_format,
        )
        async for chunk in audio_stream:
            yield chunk
