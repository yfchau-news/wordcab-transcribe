# Copyright (c) 2023, The Wordcab team. All rights reserved.
"""Utils module of the Wordcab ASR API."""

import asyncio
import subprocess
from pathlib import Path
from typing import List

from yt_dlp import YoutubeDL


async def run_subprocess(command: List[str]) -> tuple:
    """
    Run a subprocess asynchronously.

    Args:
        command (List[str]): Command to run.

    Returns:
        tuple: Tuple with the return code, stdout and stderr.
    """
    process = await asyncio.create_subprocess_exec(*command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = await process.communicate()

    return process.returncode, stdout, stderr


async def convert_file_to_wav(filepath: str) -> str:
    """
    Convert a file to wav format using ffmpeg.

    Args:
        filepath (str): Path to the file to convert.

    Returns:
        str: Path to the converted file.
    """
    if isinstance(filepath, str):
        filepath = Path(filepath)

    if not filepath.exists():
        raise FileNotFoundError(f"File {filepath} does not exist.")

    new_filepath = filepath.with_suffix(".wav")
    cmd = [
        "ffmpeg", "-i", str(filepath), "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", "-y", str(new_filepath)
    ]
    result = await run_subprocess(cmd)
    
    if result[0] != 0:
        raise Exception(f"Error converting file {filepath} to wav format: {result[2]}")

    return str(new_filepath)


async def download_file_from_youtube(url: str, filename: str) -> str:
    """
    Download a file from YouTube using youtube-dl.

    Args:
        url (str): URL of the YouTube video.
        filename (str): Filename to save the file as.

    Returns:
        str: Path to the downloaded file.
    """
    with YoutubeDL(
        {
            "format": "bestaudio",
            "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "wav"}],
            "outtmpl": f"{filename}",
        }
    ) as ydl:
        ydl.download([url])

    return filename + ".wav"


def delete_file(filepath: str) -> None:
    """
    Delete a file.

    Args:
        filepath (str): Path to the file to delete.
    """
    if isinstance(filepath, str):
        filepath = Path(filepath)

    if filepath.exists():
        filepath.unlink()


def format_segments(segments: list, use_dict: bool = False, include_words: bool = False) -> list:
    """
    Format the segments to a list of dicts with start, end and text keys.

    Args:
        segments (list): List of segments.
        use_dict (bool, optional): Use dict instead of object. Defaults to False.
        include_words (bool, optional): Include words. Defaults to False.

    Returns:
        list: List of dicts with start, end and text keys.
    """
    formatted_segments = []

    for segment in segments:
        segment_dict = {}

        if use_dict:
            segment_dict["start"] = segment["start"]
            segment_dict["end"] = segment["end"]
            segment_dict["text"] = segment["text"].strip()

        else:
            segment_dict["start"] = segment.start
            segment_dict["end"] = segment.end
            segment_dict["text"] = segment.text.strip()

        if include_words:
            words = [
                {
                    "start": word.start,
                    "end": word.end,
                    "word": word.word.strip(),
                    "probability": word.probability
                } 
                for word in segment.words
            ]
            segment_dict["words"] = words

        formatted_segments.append(segment_dict)

    return formatted_segments