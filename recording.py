import sounddevice as sd
import numpy as np
import wave
from pydub import AudioSegment
import os

# Funkcja do nagrywania dźwięku
def record_audio(duration, filename="output.wav", samplerate=44100, channels=1):
    print("Nagrywanie rozpoczęte...")

    # Nagrywanie dźwięku
    recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=channels, dtype='int16')
    sd.wait()  # Oczekiwanie na zakończenie nagrywania

    print("Nagrywanie zakończone.")

    # Zapisz nagranie jako plik WAV
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)  # 2 bajty na próbkę (16 bitów)
        wf.setframerate(samplerate)
        wf.writeframes(recording.tobytes())

    return filename

# Funkcja do konwersji pliku WAV do MP3
def convert_to_mp3(wav_filename, mp3_filename="output.mp3"):
    print(f"Konwersja pliku {wav_filename} do formatu MP3...")

    # Konwersja WAV do MP3 za pomocą Pydub
    audio = AudioSegment.from_wav(wav_filename)
    audio.export(mp3_filename, format="mp3")

    print(f"Plik zapisany jako {mp3_filename}")

# Główna funkcja do nagrywania i zapisywania w formacie MP3
def main():
    duration = int(input("Podaj czas nagrywania w sekundach: "))  # Czas nagrania w sekundach
    wav_file = record_audio(duration)

    # Zapisz plik MP3
    convert_to_mp3(wav_file)

    # Usuń plik WAV, jeśli nie jest potrzebny
    if os.path.exists(wav_file):
        os.remove(wav_file)
        print(f"Plik {wav_file} został usunięty.")

if __name__ == "__main__":
    main()