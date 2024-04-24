import os
import json
import requests

soundfile = "transcription_4.mp3"
json_folder_path = "json_outputs"
docker_container_port = 5001

filepath = os.path.join(os.path.dirname(__file__), "soundfiles", soundfile)  # or any other convertible format by ffmpeg
print(filepath)

data = {
  "num_speakers": -1,  # # Leave at -1 to guess the number of speakers
  "diarization": True,  # Longer processing time but speaker segment attribution
  "multi_channel": False,  # Only for stereo audio files with one speaker per channel
  "source_lang": "zh",  # optional, default is "en"
  "timestamps": "s",  # optional, default is "s". Can be "s", "ms" or "hms".
  "word_timestamps": True,  # optional, default is False
}

with open(filepath, "rb") as f:
    files = {"file": f}
    response = requests.post(
        f"http://localhost:{docker_container_port}/api/v1/audio",
        files=files,
        data=data,
    )

r_json = response.json()
filename = soundfile.split(".")[0]

os.makedirs(json_folder_path, exist_ok=True)
output_file_path = os.path.join(json_folder_path, f"{filename}.json")

with open(output_file_path, "w", encoding="utf-8") as f:
  json.dump(r_json, f, indent=4, ensure_ascii=False)