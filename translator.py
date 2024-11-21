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
    """
    Starts recording audio, processes it with speech recognition, and translates it.
    The recognized and translated text is placed in the `output_queue`.
    """
    global recording
    recording = True
    print("Recording started...")

    # Use a separate thread for non-blocking recording
    def record_and_translate():
        with sr.Microphone() as source:
            try:
                recognizer.adjust_for_ambient_noise(source, duration=1)
                print("Microphone adjusted for ambient noise.")
                while recording:
                    try:
                        print("Listening for speech...")
                        audio = recognizer.listen(source, timeout=5)
                        original_text = recognizer.recognize_google(audio)
                        print(f"Original text: {original_text}")

                        # Translate the recognized text
                        translated_text = translate_text(original_text, target_language)
                        output_queue.put((original_text, translated_text))
                        print(f"Translated text: {translated_text}")
                    except sr.UnknownValueError:
                        print("Could not understand the audio.")
                        output_queue.put(("Could not understand audio", ""))
                    except sr.WaitTimeoutError:
                        print("No speech detected within the timeout period.")
                        output_queue.put(("No speech detected", ""))
                    except Exception as e:
                        print(f"Error during speech recognition: {e}")
                        output_queue.put(("Recognition error", ""))
            except Exception as mic_error:
                print(f"Microphone error: {mic_error}")
                output_queue.put(("Microphone error", ""))
            finally:
                print("Stopped listening.")

    threading.Thread(target=record_and_translate, daemon=True).start()

def stop_recording():
    """
    Stops the recording process by setting the global `recording` flag to False.
    """
    global recording
    recording = False
    print("Recording stopped.")

def translate_text(text, target_language):
    """
    Translates the given text to the specified target language.
    """
    try:
        result = translator.translate(text, dest=target_language)
        return result.text
    except Exception as e:
        print(f"Error in translation: {e}")
        return "Translation error"
