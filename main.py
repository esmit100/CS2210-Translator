from gtts import gTTS
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.uix.image import Image
import translator
import threading
from googletrans import LANGUAGES
from kivy.core.window import Window
from playsound import playsound
import os
from kivy.uix.dropdown import DropDown


# Configure window properties
Window.size = (800, 480)
Window.fullscreen = True
Window.clearcolor = (0.1, 0.2, 0.3, 1)  # Subtle dark blue background


class RootWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 10
        self.padding = [20, 20, 20, 20]
        self.selected_language = 'es'  # Default language is Spanish

        # Background Image
        self.add_widget(Image(
            source='Translator2.jpg',  # Replace with your image path
            allow_stretch=True,
            keep_ratio=False
        ))

        # Header Label
        header_label = Label(
            text="Natural Language Translator",
            font_size='50sp',
            bold=True,
            color=(1, 1, 1, 1),
            size_hint=(1, None),
            height=60
        )
        self.add_widget(header_label)

        # Language Selection
        dropdown_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=50, spacing=10)
        self.language_button = Button(
            text="Select Language (Default: Spanish)",
            size_hint=(0.7, 1),
            background_color=(0.2, 0.5, 0.8, 1),
            bold=True
        )
        self.language_button.bind(on_release=self.create_dropdown)
        dropdown_layout.add_widget(self.language_button)

        self.exit_button = Button(
            text="EXIT",
            size_hint=(0.3, 1),
            background_color=(0.8, 0.2, 0.2, 1),
            bold=True
        )
        self.exit_button.bind(on_press=self.exit_app)
        dropdown_layout.add_widget(self.exit_button)

        self.add_widget(dropdown_layout)

        # Scrollable Text Area
        scroll_view = ScrollView(size_hint=(1, 1))
        content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10)
        content.bind(minimum_height=content.setter('height'))

        # Original and Translated Texts
        self.input_label = Label(
            text="Original input will appear here.",
            size_hint=(1, None),
            height=70,
            halign='center',
            valign='middle',
            font_size='18sp',
            bold=True,
            color=(1, 1, 1, 1)
        )
        self.input_label.bind(size=self.input_label.setter('text_size'))
        content.add_widget(self.input_label)

        self.translation_label = Label(
            text="Translated text will appear here.",
            size_hint=(1, None),
            height=70,
            halign='center',
            valign='middle',
            font_size='18sp',
            bold=True,
            color=(0.9, 0.9, 0.2, 1)
        )
        self.translation_label.bind(size=self.translation_label.setter('text_size'))
        content.add_widget(self.translation_label)

        # Start/Stop Recording Button
        self.record_button = Button(
            text="🎙️ Start Recording",
            size_hint=(1, None),
            height=60,
            background_color=(0.1, 0.7, 0.3, 1),
            bold=True,
            font_size='18sp'
        )
        self.record_button.bind(on_press=self.toggle_recording)
        content.add_widget(self.record_button)

        scroll_view.add_widget(content)
        self.add_widget(scroll_view)

        # Schedule a clock to check the queue for new translations
        Clock.schedule_interval(self.update_texts_from_queue, 0.5)

    def create_dropdown(self, instance):
        """Creates a dropdown menu for language selection."""
        self.language_dropdown = DropDown()
        for lang_code, lang_name in LANGUAGES.items():
            btn = Button(
                text=lang_name.capitalize(),
                size_hint_y=None,
                height=44,
                background_color=(0.2, 0.5, 0.8, 1)
            )
            btn.bind(on_release=lambda btn, code=lang_code: self.select_language(code, btn.text))
            self.language_dropdown.add_widget(btn)
        self.language_dropdown.open(instance)

    def select_language(self, lang_code, lang_name):
        """Select a language for translation."""
        self.selected_language = lang_code
        self.language_button.text = f"Language: {lang_name}"
        self.language_dropdown.dismiss()

    def toggle_recording(self, instance):
        """Start or stop the recording and translation process."""
        if not translator.recording:
            self.record_button.text = 'Stop Recording'
            threading.Thread(target=translator.start_recording, args=(self.selected_language,), daemon=True).start()
        else:
            self.record_button.text = 'Start Recording'
            translator.stop_recording()

    def update_texts_from_queue(self, dt):
        """Update the displayed texts from the translator's output queue."""
        try:
            while not translator.output_queue.empty():
                original_text, translated_text = translator.output_queue.get_nowait()
                self.input_label.text = f"Original: {original_text}"
                self.translation_label.text = f"Translation: {translated_text}"
                self.play_translated_audio(translated_text, self.selected_language)
        except Exception as e:
            print(f"Error updating texts: {e}")

    def play_translated_audio(self, text, lang):
        """Play the translated text as audio."""
        try:
            tts = gTTS(text=text, lang=lang)
            audio_file = "/tmp/translated_audio.mp3"
            tts.save(audio_file)
            playsound(audio_file)
        except Exception as e:
            print(f"Error in audio playback: {e}")

    def exit_app(self, instance):
        """Exit the application."""
        translator.stop_recording()  # Ensure the recording is stopped
        App.get_running_app().stop()  # Stop the Kivy app
        print("Application exited.")


class TranslatorApp(App):
    def build(self):
        return RootWidget()


if __name__ == '__main__':
    os.environ["DISPLAY"] = ":0"  # Necessary for Raspberry Pi
    TranslatorApp().run()
