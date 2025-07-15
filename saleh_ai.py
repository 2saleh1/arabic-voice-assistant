import cohere
import sounddevice as sd
import numpy as np
import wave
import threading
import time
from gtts import gTTS
import pygame
import io
import os
from RealtimeSTT import AudioToTextRecorder
from multiprocessing import freeze_support

# Initialize Cohere client
co = cohere.Client('COHERE_API_KEY')  # Your API key

# Initialize pygame mixer
pygame.mixer.init()

# Global recorder variable
recorder = None

def initialize_recorder():
    """Initialize RealtimeSTT recorder"""
    global recorder
    recorder = AudioToTextRecorder(
        model="small",  # Use tiny model for faster processing
        # Arabic language
        # Available models: tiny, base, small, medium, large
        spinner=False,
        use_microphone=True,
        silero_sensitivity=0.4,
        webrtc_sensitivity=2,
        post_speech_silence_duration=0.7,
        min_length_of_recording=0.5,
        min_gap_between_recordings=0,
        enable_realtime_transcription=False,
        realtime_processing_pause=0.2,
        realtime_model_type='tiny'
    )

def speak(text):
    """Convert text to speech and play it immediately"""
    try:
        tts = gTTS(text=text, lang='ar')
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        
        pygame.mixer.music.load(mp3_fp)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    except Exception as e:
        print(f"حدث خطأ في تحويل النص إلى كلام: {e}")

def record_and_transcribe():
    """Record audio and transcribe using RealtimeSTT"""
    try:
        print("جاري التسجيل... تحدث الآن")
        text = recorder.text()
        print("انتهى التسجيل")
        return text
    except Exception as e:
        print(f"حدث خطأ في التسجيل أو التعرف على الكلام: {e}")
        return ""

def generate_response(prompt):
    """Generate response using Cohere's Arabic model with Chat API"""
    try:
        response = co.chat(
            model="command-r7b-arabic-02-2025",
            message=prompt,
            max_tokens=200,
            temperature=0.7
        )
        return response.text.strip()
    except Exception as e:
        print(f"حدث خطأ في توليد الرد: {e}")
        return "عذرًا، حدث خطأ أثناء معالجة طلبك."

def conversation_loop():
    """Main conversation loop"""
    print("صالح: أهلاً وسهلاً! أنا صالح، كيف يمكنني مساعدتك اليوم؟")
    speak("أهلاً وسهلاً! أنا صالح، كيف يمكنني مساعدتك اليوم؟")
    
    while True:
        try:
            # Record and transcribe audio
            user_input = record_and_transcribe()
            
            if not user_input or user_input.strip() == "":
                print("صالح: لم أسمعك بوضوح، هل يمكنك التكرار؟")
                speak("لم أسمعك بوضوح، هل يمكنك التكرار؟")
                continue
                
            print(f"أنت: {user_input}")
            
            # Check for exit commands
            if any(word in user_input.lower() for word in ["وداعا", "مع السلامة", "إنهاء", "توقف", "exit"]):
                print("صالح: وداعاً! أتمنى لك يوماً سعيداً.")
                speak("وداعاً! أتمنى لك يوماً سعيداً.")
                break
            
            # Generate response
            prompt = f"أنت مساعد عربي اسمه صالح. أنت لطيف ومفيد. المستخدم يقول: '{user_input}'. الرد بطريقة مناسبة."
            ai_response = generate_response(prompt)
            print(f"صالح: {ai_response}")
            
            # Speak response
            speak(ai_response)
            
        except KeyboardInterrupt:
            print("\nصالح: وداعاً! أتمنى لك يوماً سعيداً.")
            speak("وداعاً! أتمنى لك يوماً سعيداً.")
            break
        except Exception as e:
            print(f"حدث خطأ غير متوقع: {e}")
            speak("حدث خطأ تقني، أحاول إعادة الاتصال")
            time.sleep(1)

if __name__ == "__main__":
    freeze_support()  # Required for Windows multiprocessing
    
    print("جاري تحضير النظام...")
    
    # Print available audio devices
    print("الأجهزة الصوتية المتاحة:")
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        print(f"{i}: {device['name']}")
    
    print(f"\nسيتم استخدام الميكروفون الافتراضي للنظام")
    
    # Initialize recorder after freeze_support
    print("جاري تهيئة نظام التعرف على الكلام...")
    initialize_recorder()
    
    print("النظام جاهز للاستخدام!")
    
    conversation_loop()