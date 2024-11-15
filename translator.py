import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS
import os
import threading
from queue import Queue

# Global flag and queue for controlling and transferring data
recording = False
output_queue = Queue()  # Queue to hold recognized and translated text for the Kivy app

def recognize_speech(target_language='es'):
    global recording
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 300  # Adjust as needed
    recognizer.dynamic_energy_threshold = False  # Fixed threshold to avoid calibration issues

    with sr.Microphone() as source:
        print("Listening... Speak continuously, and press 'Stop Recording' to end.")

        while recording:
            try:
                # Listen to a phrase, then process and translate it
                audio = recognizer.listen(source, timeout=None, phrase_time_limit=5)  # Adjust as needed
                text = recognizer.recognize_google(audio)
                if not text.strip():
                    raise ValueError("No valid input detected.")
                print(f"You said: {text}")

                # Translate and store the detected phrase
                translated_text = translate_text(text, target_language)
                output_queue.put((text, translated_text))  # Send both texts to the main app

            except sr.UnknownValueError:
                print("Sorry, I didn't catch that.")
                output_queue.put(("No speech detected", ""))
            except sr.RequestError as e:
                print(f"Speech recognition failed: {e}")
                output_queue.put(("Recognition error", ""))
                break
            except ValueError as e:
                print(e)
                output_queue.put(("No valid input", ""))

def translate_text(text, target_lang='es'):
    translator = Translator()
    try:
        translation = translator.translate(text, dest=target_lang)
        print(f"Translated to: {translation.text}")
        return translation.text
    except Exception as e:
        print(f"Translation failed: {e}")
        return "Translation error"

def start_recording(target_language='es'):
    global recording
    recording = True
    threading.Thread(target=recognize_speech, args=(target_language,)).start()

def stop_recording():
    global recording
    recording = False
