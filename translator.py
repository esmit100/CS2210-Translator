 import speech_recognition as sr
from googletrans import Translator
from queue import Queue
import threading

# Global variables
recording = False
output_queue = Queue()  # Queue to hold recognized and translated text for the Kivy app
translator = Translator()
recognizer = sr.Recognizer()

def start_recording(target_language):
    global recording
    recording = True
    print("Recording started...")

    # Use a separate thread for non-blocking recording
    def record_and_translate():
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)
            print("Microphone ready.")
            while recording:
                try:
                    print("Listening...")
                    audio = recognizer.listen(source, timeout=5)
                    original_text = recognizer.recognize_google(audio)
                    print(f"Original: {original_text}")
                    translated_text = translate_text(original_text, target_language)
                    output_queue.put((original_text, translated_text))
                    print(f"Translated: {translated_text}")
                except sr.UnknownValueError:
                    print("Could not understand audio")
                    output_queue.put(("No speech detected", ""))
                except sr.WaitTimeoutError:
                    print("Timeout reached, no speech detected")
                except Exception as e:
                    print(f"Error during speech recognition: {e}")
                    output_queue.put(("Recognition error", ""))

    threading.Thread(target=record_and_translate, daemon=True).start()

def stop_recording():
    global recording
    recording = False
    print("Recording stopped.")

def translate_text(text, target_language):
    try:
        result = translator.translate(text, dest=target_language)
        return result.text
    except Exception as e:
        print(f"Error in translation: {e}")
        return "Translation error"
