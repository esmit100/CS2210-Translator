from gtts import gTTS
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.clock import Clock
import translator
import threading
from queue import Empty
from googletrans import LANGUAGES
from kivy.core.window import Window
from playsound import playsound
import os
from kivy.uix.dropdown import DropDown
# Ensure proper window configuration for Raspberry Pi
Window.size = (800, 480)  # Set resolution for Raspberry Pi screen
Window.fullscreen = False
Window.clearcolor = (0.9, 0.9, 0.95, 1)

class RootWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 5
        self.padding = [10, 10, 10, 10]
        self.selected_language = 'es'

        # Scrollable Layout
        scroll_view = ScrollView(size_hint=(1, None), size=(Window.width, Window.height))
        content = BoxLayout(orientation='vertical', size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))

        # Header Label
        header_label = Label(
            text="Voice Translator",
            font_size='20sp',
            size_hint=(1, None),
            height=50
        )
        content.add_widget(header_label)

        # Language Dropdown
        self.language_dropdown = DropDown()
        for lang_code, lang_name in LANGUAGES.items():
            btn = Button(
                text=lang_name.capitalize(),
                size_hint_y=None,
                height=44
            )
            btn.bind(on_release=lambda btn, code=lang_code: self.select_language(code, btn.text))
            self.language_dropdown.add_widget(btn)

        self.language_button = Button(
            text="Select Language (Default: Spanish)",
            size_hint=(1, None),
            height=40
        )
        self.language_button.bind(on_release=self.language_dropdown.open)
        content.add_widget(self.language_button)
         # Input and Translation Labels
        self.input_label = Label(
            text="Original input will appear here.",
            size_hint=(1, None),
            height=50,
            font_size='18sp'
        )
        content.add_widget(self.input_label)

        self.translation_label = Label(
            text="Translated text will appear here.",
            size_hint=(1, None),
            height=50,
            font_size='18sp'
        )
        content.add_widget(self.translation_label)

        # Recording Button
        self.record_button = Button(
            text="Start Recording",
            size_hint=(1, None),
            height=50,
            background_color=(0.1, 0.6, 0.3, 1)
        )
        self.record_button.bind(on_press=self.toggle_recording)
        content.add_widget(self.record_button)

        # Add content to ScrollView
        scroll_view.add_widget(content)
        self.add_widget(scroll_view)

        # Check queue for new translations
        Clock.schedule_interval(self.update_texts_from_queue, 0.5)

    def select_language(self, lang_code, lang_name):
        self.selected_language = lang_code
        self.language_button.text = f"Language: {lang_name}"
        self.language_dropdown.dismiss()

    def toggle_recording(self, instance):
        if not translator.recording:
            self.record_button.text = 'Stop Recording'
            threading.Thread(target=translator.start_recording, args=(self.selected_language,), daemon=True).start()
        else:
            self.record_button.text = 'Start Recording'
            translator.stop_recording()

    def update_texts_from_queue(self, dt):
        try:
            while not translator.output_queue.empty():
                original_text, translated_text = translator.output_queue.get_nowait()
                self.input_label.text = f"Original: {original_text}"
                self.translation_label.text = f"Translation: {translated_text}"
                self.play_translated_audio(translated_text, self.selected_language)
        except Exception as e:
            print(f"Error updating texts: {e}")
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
        return RootWidget()

if __name__ == '__main__':
    os.environ["DISPLAY"] = ":0"
    TranslatorApp().run()
