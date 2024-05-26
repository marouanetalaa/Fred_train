import os
from pytube import YouTube
from faster_whisper import WhisperModel
from pyannote.audio import Pipeline

def download_youtube_video(url, output_path):
    yt = YouTube(url)
    stream = yt.streams.filter(only_audio=True).first()
    audio_path = stream.download(output_path=output_path)
    return audio_path

def transcribe_audio(audio_path):
    model = WhisperModel("large-v2")
    segments, info = model.transcribe(audio_path, language="fr", condition_on_previous_text=False)
    return segments

def diarize_audio(audio_path, auth_token):
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", use_auth_token=auth_token)
    diarization_result = pipeline({"uri": "audio", "audio": audio_path})
    return diarization_result

def format_results(transcription_segments, diarization_result):
    messages = []
    for segment in transcription_segments:
        start, end, text = segment.start, segment.end, segment.text
        speaker = "user" if "SPEAKER_00" in [label for _, _, label in diarization_result.itertracks(yield_label=True) if start <= _ < end] else "assistant"
        messages.append({
            "role": speaker,
            "content": text
        })
    return messages

def save_to_json(data, output_file):
    import json
    with open(output_file, "w") as f:
        json.dump(data, f, indent=2)

def main():
    youtube_url = "https://www.youtube.com/watch?v=Lqz63RA4Qgs&list=PLIy2m_71J_WVsq0WFL4mBVmzfhIvsPlfV&index=6"
    output_path = "/home/mistral46/diar/"
    auth_token = "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"

    audio_path = download_youtube_video(youtube_url, output_path)
    transcription_segments = transcribe_audio(audio_path)
    diarization_result = diarize_audio(audio_path, auth_token)
    
    messages = format_results(transcription_segments, diarization_result)
    dataset = {"messages": messages}
    
    save_to_json(dataset, "/home/mistral46/diar/dataset.json")

if __name__ == "__main__":
    main()
