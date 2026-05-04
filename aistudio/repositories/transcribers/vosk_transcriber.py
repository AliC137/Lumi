"""
Сервис яндек speech to text
"""
import wave
import json
from pathlib import Path
from aistudio.config.config import S3Config
from vosk import Model, KaldiRecognizer
from scipy.signal import resample
import uuid
import numpy as np
from pydub import AudioSegment
import locale


# Construct path to model: one level up from project root
vosk_model = Model("aimodels/vosk-model-tg-0.22")

class VoskTranscriber:
    def __init__(self, config: S3Config = None):
        """
        Конструктор
        """
    def _check_locale(self):
        current_locale = locale.getlocale()

        print(f"Current Locale: {current_locale}")
        try:
            locale.setlocale(locale.LC_ALL, "")
        except locale.Error as e:
            print(f"Locale setting error: {e}. Using default '.' fallback.")
            # Fallback to standard '.' if system locale is unsupported
            decimal_delimiter = '.'
        else:
            # Get the dictionary of local conventions and extract the decimal point character
            conv = locale.localeconv()
            decimal_delimiter = conv['decimal_point']

        #print(f"The local decimal delimiter is: '{decimal_delimiter}'")

    def _change_wav_framerate(self, input_filepath, new_framerate):
        """
        Changes the framerate of a WAV file and saves it to a new file.

        Args:
            input_filepath (str): Path to the input WAV file.
            new_framerate (int): The desired new framerate in Hz.
        """
        out_file_path = f'tmp/{uuid.uuid4()}.wav'
        output_filepath = Path(out_file_path)

        with wave.open(input_filepath, 'rb') as infile:
            # Get original audio parameters
            nchannels = infile.getnchannels()
            sampwidth = infile.getsampwidth()
            original_framerate = infile.getframerate()
            nframes = infile.getnframes()

            # Read audio data
            audio_bytes = infile.readframes(nframes)

            # Convert to numpy array
            # Assuming 16-bit signed integers for simplicity; adjust dtype if needed
            dtype = np.int16 if sampwidth == 2 else np.int32 if sampwidth == 4 else np.int8
            audio_data = np.frombuffer(audio_bytes, dtype=dtype)

            # Resample the audio data if the framerate needs to change
            if original_framerate != new_framerate:
                num_samples_new = int(len(audio_data) * (new_framerate / original_framerate))
                audio_data_resampled = resample(audio_data, num_samples_new)

                # Convert back to original data type if necessary (resample returns float)
                audio_data_resampled = audio_data_resampled.astype(dtype)
            else:
                audio_data_resampled = audio_data

        # Write the resampled audio to a new WAV file
        with wave.open(out_file_path, 'wb') as outfile:
            outfile.setnchannels(nchannels)
            outfile.setsampwidth(sampwidth)
            outfile.setframerate(new_framerate)
            outfile.writeframes(audio_data_resampled.tobytes())
        return output_filepath
    def _mono(self, input_filepath):
        out_file_path = f'tmp/{uuid.uuid4()}.wav'
        sound = AudioSegment.from_file(str(input_filepath))
        sound = sound.set_channels(1).set_frame_rate(16000)
        sound.export(out_file_path, format="wav")
        return Path(out_file_path)
    def transcribe(self, path_file: Path) -> str:
        """
        Перевести файл в текст
        """
        path_file = self._mono(str(path_file))
        #path_file = self._change_wav_framerate(str(path_file), 16000)
        self._check_locale()
        with path_file.open("rb") as file:
            with wave.open(file, 'rb') as wf:
                rec = KaldiRecognizer(vosk_model, wf.getframerate())
                rec.SetWords(True)
                rec.SetPartialWords(True)
                results = []
                while True:
                    data = wf.readframes(4000)
                    if len(data) == 0:
                        break
                    if rec.AcceptWaveform(data):
                        results.append(json.loads(rec.Result()))
                    #else:
                        # Partial result available (optional)
                        #partial_result = json.loads(rec.PartialResult())
                        #result = {"text": partial_result['partial']}
                        #results.append(result)
                        #print(f"Partial: {partial_result['partial']}")
                try:
                    final_result = rec.FinalResult()
                    print(f"final_result = {final_result}")
                    json_final_result = json.loads(final_result)
                    print(f"json_final_result = {json_final_result}")
                    results.append(json_final_result)
                except Exception as e:
                    print(f"vosk Exception {e}")
                self._check_locale()
                #    pass
                self._check_locale()
                full_text = " ".join(r.get("text", "") for r in results)
                return full_text
