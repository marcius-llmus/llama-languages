import asyncio
import base64
import json
import typing
import urllib.parse

import websockets
from elevenlabs.core.api_error import ApiError
from elevenlabs.core.client_wrapper import AsyncClientWrapper
from elevenlabs.core.jsonable_encoder import jsonable_encoder
from elevenlabs.core.remove_none_from_dict import remove_none_from_dict
from elevenlabs.core.request_options import RequestOptions
from elevenlabs.text_to_speech.client import AsyncTextToSpeechClient
from elevenlabs.types import OutputFormat, VoiceSettings

# this is used as the default value for optional parameters
OMIT = typing.cast(typing.Any, ...)


async def text_chunker(
    chunks: typing.AsyncIterator[str],
) -> typing.AsyncIterator[str]:
    """Used during input streaming to chunk text blocks and set last char to space"""
    splitters = (".", ",", "?", "!", ";", ":", "—", "-", "(", ")", "[", "]", "}", " ")
    buffer = ""
    async for text in chunks:
        if buffer.endswith(splitters):
            yield buffer if buffer.endswith(" ") else buffer + " "
            buffer = text
        elif text.startswith(splitters):
            output = buffer + text[0]
            yield output if output.endswith(" ") else output + " "
            buffer = text[1:]
        else:
            buffer += text
    if buffer != "":
        yield buffer + " "


class AsyncRealtimeTextToSpeechClient(AsyncTextToSpeechClient):
    def __init__(self, *, client_wrapper: AsyncClientWrapper):
        super().__init__(client_wrapper=client_wrapper)
        self._ws_base_url = (
            urllib.parse.urlparse(self._client_wrapper.get_environment().base)
            ._replace(scheme="wss")
            .geturl()
        )

    async def convert_realtime(
        self,
        voice_id: str,
        *,
        text: typing.AsyncIterator[str],
        model_id: typing.Optional[str] = OMIT,
        output_format: typing.Optional[OutputFormat] = "mp3_44100_128",
        voice_settings: typing.Optional[VoiceSettings] = OMIT,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.AsyncIterator[bytes]:
        """
        Asynchronously converts text into speech using a voice of your choice and returns audio.
        This is a patched, async-native version of the synchronous `convert_realtime` method.
        """
        url = urllib.parse.urljoin(
            self._ws_base_url,
            f"v1/text-to-speech/{jsonable_encoder(voice_id)}/stream-input?model_id={model_id}&output_format={output_format}",
        )
        headers = remove_none_from_dict(
            {
                **self._client_wrapper.get_headers(),
                **(
                    request_options.get("additional_headers", {})
                    if request_options is not None
                    else {}
                ),
            }
        )

        async with websockets.connect(
            url, additional_headers=jsonable_encoder(headers)
        ) as socket:
            try:
                await socket.send(
                    json.dumps(
                        dict(
                            text=" ",
                            try_trigger_generation=True,
                            voice_settings=voice_settings.dict()
                            if voice_settings
                            else None,
                            generation_config=dict(
                                chunk_length_schedule=[50],
                            ),
                        )
                    )
                )
            except websockets.exceptions.ConnectionClosedError as ce:
                raise ApiError(body=ce.reason, status_code=ce.code)

            data: dict = {}
            try:
                async for text_chunk in text_chunker(text):
                    data = dict(text=text_chunk, try_trigger_generation=True)
                    await socket.send(json.dumps(data))
                    try:
                        response = await asyncio.wait_for(socket.recv(), timeout=1e-2)
                        data = json.loads(response)
                        if "audio" in data and data["audio"]:
                            yield base64.b64decode(data["audio"])  # type: ignore
                    except asyncio.TimeoutError:
                        pass

                await socket.send(json.dumps(dict(text="")))

                while True:
                    response = await socket.recv()
                    data = json.loads(response)
                    if "audio" in data and data["audio"]:
                        yield base64.b64decode(data["audio"])  # type: ignore
            except websockets.exceptions.ConnectionClosed as ce:
                if "message" in data:
                    raise ApiError(body=data, status_code=ce.code)
                elif ce.code != 1000:
                    raise ApiError(body=ce.reason, status_code=ce.code)