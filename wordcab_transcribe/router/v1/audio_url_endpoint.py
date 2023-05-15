# Copyright 2023 The Wordcab Team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Audio url endpoint for the Wordcab Transcribe API."""

from typing import Optional

import shortuuid
from fastapi import APIRouter, BackgroundTasks
from fastapi import status as http_status

from wordcab_transcribe.dependencies import asr
from wordcab_transcribe.models import ASRResponse, DataRequest
from wordcab_transcribe.utils import (
    convert_file_to_wav,
    convert_timestamp,
    delete_file,
    download_audio_file,
    format_punct,
    is_empty_string,
)


router = APIRouter()


@router.post("", response_model=ASRResponse, status_code=http_status.HTTP_200_OK)
async def inference_with_audio_url(
    background_tasks: BackgroundTasks,
    url: str,
    data: Optional[DataRequest] = None,
) -> ASRResponse:
    """Inference endpoint with audio url."""
    filename = f"audio_url_{shortuuid.ShortUUID().random(length=32)}"
    filepath = await download_audio_file(url, filename)
    extension = filepath.split(".")[-1]

    if extension != "wav":
        filepath = await convert_file_to_wav(filepath)
        background_tasks.add_task(delete_file, filepath=f"{filename}.{extension}")
    else:
        filepath = filename

    if data is None:
        data = DataRequest()
    else:
        data = DataRequest(**data.dict())

    raw_utterances = await asr.process_input(filepath, data.source_lang, data.alignment)

    timestamps_format = data.timestamps
    utterances = [
        {
            "text": format_punct(utterance["text"]),
            "start": convert_timestamp(utterance["start"], timestamps_format),
            "end": convert_timestamp(utterance["end"], timestamps_format),
            "speaker": int(utterance["speaker"]),
        }
        for utterance in raw_utterances
        if not is_empty_string(utterance["text"])
    ]

    background_tasks.add_task(delete_file, filepath=filepath)

    return ASRResponse(
        utterances=utterances,
        alignment=data.alignment,
        source_lang=data.source_lang,
        timestamps=data.timestamps,
    )