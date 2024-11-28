import os
import threading
import tempfile
from playsound import playsound
from gtts import gTTS
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.dropdown import DropDown
from googletrans import LANGUAGES, Translator
import speech_recognition as sr

# Configure window properties
Window.size = (800, 480)
Window.fullscreen = True
Window.clearcolor = (0.1, 0.2, 0.3, 1)

# Global variables
recording_flag = threading.Event()  # Event to manage recording state safely
speech_text = ""  # To store the recognized speech text


class RootWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 10
        self.padding = [20, 20, 20, 20]
        self.selected_language = 'es'  # Default language is Spanish
        self.audio_file = None

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

        # Start Recording Button
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

        # Translate Button
        self.translate_button = Button(
            text="🌐 Translate",
            size_hint=(1, None),
            height=60,
            background_color=(0.2, 0.5, 0.8, 1),
            bold=True,
            font_size='18sp'
        )
        self.translate_button.bind(on_press=self.translate_text)
        content.add_widget(self.translate_button)

        scroll_view.add_widget(content)
        self.add_widget(scroll_view)

    def create_dropdown(self, instance):
        """Creates a dropdown menu for language selection with spacing between options."""
        self.language_dropdown = DropDown(auto_width=False)

        # Create a container with spacing for the dropdown
        dropdown_container = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10)
        dropdown_container.bind(minimum_height=dropdown_container.setter('height'))

        for lang_code, lang_name in LANGUAGES.items():
            # Create a button for each language
            btn = Button(
                text=lang_name.capitalize(),
                size_hint_y=None,
                height=50,
                background_color=(0.2, 0.5, 0.8, 1)
            )
            btn.bind(on_release=lambda btn, code=lang_code: self.select_language(code, btn.text))
            dropdown_container.add_widget(btn)

        # Wrap the container in a ScrollView for touch-friendly scrolling
        scroll_view = ScrollView(size_hint=(1, None), height=300, do_scroll_x=False, do_scroll_y=True)
        scroll_view.add_widget(dropdown_container)

        # Add ScrollView to the dropdown
        self.language_dropdown.add_widget(scroll_view)

        # Open the dropdown menu
        self.language_dropdown.open(instance)

    def select_language(self, lang_code, lang_name):
        """Select a language for translation."""
        self.selected_language = lang_code
        self.language_button.text = f"Language: {lang_name}"
        self.language_dropdown.dismiss()

    def toggle_recording(self, instance):
        """Start or stop the recording process."""
        if not recording_flag.is_set():
            recording_flag.set()
            self.record_button.text = 'Stop Recording'
            threading.Thread(target=self.record_speech, daemon=True).start()
        else:
            recording_flag.clear()
            self.record_button.text = 'Start Recording'

    def record_speech(self):
        """Continuously record speech from the microphone and convert it to text."""
        global speech_text
        recognizer = sr.Recognizer()
        mic = sr.Microphone()
        speech_text = ""  # Reset the speech text

        try:
            with mic as source:
                print("Adjusting for ambient noise...")
                recognizer.adjust_for_ambient_noise(source, duration=1)
                print("Start speaking...")

                while recording_flag.is_set():
                    print("Listening...")
                    audio = recognizer.listen(source, timeout=None, phrase_time_limit=5)
                    try:
                        recognized_text = recognizer.recognize_google(audio)
                        print(f"Recognized: {recognized_text}")
                        # Append recognized segment to speech_text
                        speech_text += recognized_text + " "
                        # Update the UI with partial input
                        self.input_label.text = f"Original: {speech_text.strip()}"
                    except sr.UnknownValueError:
                        print("Speech Recognition could not understand audio")
                    except sr.RequestError as e:
                        print(f"Speech Recognition API error: {e}")
        except Exception as e:
            print(f"Error during recording: {e}")

    def translate_text(self, instance):
        """Translate the captured text."""
        global speech_text
        if speech_text:
            try:
                translator = Translator()
                translated_text = translator.translate(speech_text, dest=self.selected_language).text
                self.translation_label.text = f"Translation: {translated_text}"
                self.play_translated_audio(translated_text, self.selected_language)
            except Exception as e:
                print(f"Translation Error: {e}")
                self.translation_label.text = "Translation: [Error occurred during translation]"
        else:
            self.translation_label.text = "Translation: [No text to translate]"

    def play_translated_audio(self, text, lang):
        """Play the translated text as audio."""
        try:
            if self.audio_file:
                os.remove(self.audio_file)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
                self.audio_file = temp_audio.name
                tts = gTTS(text=text, lang=lang)
                tts.save(self.audio_file)
            playsound(self.audio_file)
        except Exception as e:
            print(f"Audio playback error: {e}")

    def exit_app(self, instance):
        """Exit the application."""
        recording_flag.clear()
        if self.audio_file and os.path.exists(self.audio_file):
            os.remove(self.audio_file)
        App.get_running_app().stop()


class TranslatorApp(App):
    def build(self):
        return RootWidget()


if __name__ == '__main__':
    TranslatorApp().run()
