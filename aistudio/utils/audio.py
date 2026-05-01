import subprocess
import tempfile
from fastapi import UploadFile

def convert_to_wav_16k(upload_file: UploadFile) -> str:
    """Convert uploaded audio to 16kHz mono WAV using ffmpeg."""
    input_suffix = upload_file.filename.split('.')[-1]

    with tempfile.NamedTemporaryFile(suffix=f".{input_suffix}", delete=False) as input_temp:
        input_temp.write(upload_file.file.read())
        input_path = input_temp.name

    output_temp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    output_path = output_temp.name
    output_temp.close()

    # Use just "ffmpeg" — since your PATH is now set
    command = [
        "ffmpeg", "-y", "-i", input_path,
        "-ar", "16000", "-ac", "1",
        "-f", "wav", output_path
    ]

    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print("FFmpeg error:", result.stderr)
        raise RuntimeError("Audio conversion failed")

    return output_path
