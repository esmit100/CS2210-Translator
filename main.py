from gtts import gTTS
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.label import Label
from kivy.clock import Clock
import translator  # Custom module for translation logic
import threading
from queue import Empty
from googletrans import LANGUAGES
from kivy.core.window import Window
from playsound import playsound

# Set background color for the app window
Window.clearcolor = (0.9, 0.9, 0.95, 1)

class RootWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 10
        self.padding = [20, 20, 20, 20]
        self.selected_language = 'es'

        # Header label
        header_label = Label(
            text="Voice Translator",
            font_size=32,
            size_hint=(1, 0.2),
            bold=True
        )
        self.add_widget(header_label)

        # Language dropdown
        self.language_dropdown = DropDown()
        for lang_code, lang_name in LANGUAGES.items():
            btn = Button(text=lang_name.capitalize(), size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn, code=lang_code: self.select_language(code, btn.text))
            self.language_dropdown.add_widget(btn)

        self.language_button = Button(
            text="Select Language (Default: Spanish)",
            size_hint=(1, 0.15)
        )
        self.language_button.bind(on_release=self.language_dropdown.open)
        self.add_widget(self.language_button)

        # Input and translation labels
        self.input_label = Label(text="Original input will appear here.", size_hint=(1, 0.2))
        self.translation_label = Label(text="Translated text will appear here.", size_hint=(1, 0.2))
        self.add_widget(self.input_label)
        self.add_widget(self.translation_label)

        # Recording button
        self.record_button = Button(
            text="Start Recording",
            size_hint=(1, 0.15),
            background_color=(0.1, 0.6, 0.3, 1)
        )
        self.record_button.bind(on_press=self.toggle_recording)
        self.add_widget(self.record_button)

        # Check queue for new translations
        Clock.schedule_interval(self.update_texts_from_queue, 0.5)

    def select_language(self, lang_code, lang_name):
        self.selected_language = lang_code
        self.language_button.text = f"Language: {lang_name}"
        self.language_dropdown.dismiss()

    def toggle_recording(self, instance):
        if not translator.recording:
            self.record_button.text = 'Stop Recording'
            threading.Thread(target=translator.start_recording, args=(self.selected_language,)).start()
        else:
            self.record_button.text = 'Start Recording'
            translator.stop_recording()

    def update_texts_from_queue(self, dt):
        try:
            original_text, translated_text = translator.output_queue.get_nowait()
            self.input_label.text = f"Original: {original_text}"
            self.translation_label.text = f"Translation: {translated_text}"
            self.play_translated_audio(translated_text, self.selected_language)
        except Empty:
            pass

    def play_translated_audio(self, text, lang):
        try:
            tts = gTTS(text=text, lang=lang)
            audio_file = "/tmp/translated_audio.mp3"
            tts.save(audio_file)
            playsound(audio_file)
        except Exception as e:
            print(f"Error in audio playback: {e}")

class TranslatorApp(App):
    def build(self):
        Window.fullscreen = True
        return RootWidget()

if __name__ == '__main__':
    TranslatorApp().run()
