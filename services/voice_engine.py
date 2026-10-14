import io
import asyncio
import sounddevice as sd
import soundfile as sf
import numpy as np
import edge_tts
import speech_recognition as sr

def speak(text: str):
    """Natural Human-like HD Voice Engine for Roman Urdu"""
    if not text or not text.strip():
        return

    try:
        VOICE = "en-IN-NeerjaNeural"
        
        async def _generate_audio():
            communicate = edge_tts.Communicate(text, VOICE, rate="+0%", pitch="+0Hz")
            audio_data = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]
            return audio_data

        audio_bytes = asyncio.run(_generate_audio())

        if audio_bytes:
            audio_stream = io.BytesIO(audio_bytes)
            data, samplerate = sf.read(audio_stream)
            
            if data.ndim == 1:
                data = data.reshape(-1, 1)

            padding = np.zeros((int(samplerate * 0.2), data.shape[1]))
            full_data = np.vstack((data, padding))
            
            sd.play(full_data, samplerate)
            sd.wait()
            
    except Exception as e:
        print(f"[TTS Error]: {e}")

def listen_mic() -> str:
    """Robust sounddevice listener with detailed error logging"""
    sample_rate = 16000
    duration = 5  # 5 seconds recording window
    
    print("\n🎤 Listening... (Suno Ozain, bolein)")
    try:
        # Auto-detect default input device channels
        input_info = sd.query_devices(kind='input')
        channels = min(2, input_info.get('max_input_channels', 1))

        # Direct microphone recording via sounddevice
        recording = sd.rec(
            int(duration * sample_rate), 
            samplerate=sample_rate, 
            channels=channels, 
            dtype='int16'
        )
        sd.wait()

        # If recorded in stereo, convert to mono for speech recognition
        if channels > 1:
            recording = np.mean(recording, axis=1, dtype=np.int16)

        # Silence detector (filters out quiet background noise)
        volume_norm = np.linalg.norm(recording) / len(recording)
        if volume_norm < 0.05:
            return ""

        print("⚡ Processing Voice...")

        # Convert raw audio array into WAV format in memory
        wav_io = io.BytesIO()
        sf.write(wav_io, recording, sample_rate, format='WAV', subtype='PCM_16')
        wav_io.seek(0)

        # Process WAV stream using SpeechRecognition
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_io) as source:
            audio_data = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio_data, language="en-IN")
            except Exception:
                text = recognizer.recognize_google(audio_data, language="en-US")

            print(f"👤 Ozain: {text}")
            return text

    except Exception as e:
        print(f"[Mic Error Details]: {type(e).__name__} - {e}")
        return ""