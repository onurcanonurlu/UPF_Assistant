import pyaudio
import wave
import whisper
import requests
import json
import os
from pydub import AudioSegment
from pydub.playback import play
from gtts import gTTS
from io import BytesIO
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel
from mtranslate import translate
from transformers import pipeline


class AudioRecorder:
    def __init__(self, rate=16000, channels=1, chunk=1024, record_seconds=5, filename="recorded_audio.wav"):
        self.rate = rate
        self.channels = channels
        self.chunk = chunk
        self.record_seconds = record_seconds
        self.filename = filename
        self.filepath = os.path.abspath(os.path.join(os.path.dirname(__file__), filename))

    def record_audio(self):
        # Open PyAudio stream
        audio = pyaudio.PyAudio()
        stream = audio.open(format=pyaudio.paInt16,
                            channels=self.channels,
                            rate=self.rate,
                            input=True,
                            frames_per_buffer=self.chunk)

        print("Recording audio...")

        # Create a list to store the audio frames
        frames = []

        # Record audio for the specified number of seconds
        for i in range(0, int(self.rate / self.chunk * self.record_seconds)):
            data = stream.read(self.chunk)
            frames.append(data)

        print("Finished recording audio.")

        # Stop and close the PyAudio stream
        stream.stop_stream()
        stream.close()
        audio.terminate()

        # Write the audio frames to a WAV file
        with wave.open(self.filepath, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(frames))

        print(f"Saved audio file to {self.filepath}")
        return self.filepath
class WhisperTranscriber:
    def __init__(self, model_name="base"):
        self.model = whisper.load_model(model_name)
    def set_language(self, language):
        self.language = language
    def transcribe_eng(self, filepath):
        result = self.model.transcribe(filepath)
        text = result["text"]
        return text
    def transcribe_tur(self,filepath):
        pipe = pipeline(model="emre/whisper-medium-turkish-2")
        text = pipe(filepath)["text"]
        return text
class RasaConnector:
    def __init__(self, endpoint="http://localhost:5005/webhooks/rest/webhook", sender="test_user", language='en'):
        self.endpoint = endpoint
        self.sender = sender
        self.language = language


    def set_language(self, language):
        self.language = language

    def send_message(self, message, metadata=None):
        data = {
            "sender": self.sender,
            "message": message,
            "metadata": metadata if metadata else {}
        }
        response = requests.post(self.endpoint, json=data)
        response_data = json.loads(response.text)
        if len(response_data) > 0:
            response_text = response_data[0]['text']
            if self.language == 'tr':
                response_text = translate(response_text ,'tr','en')
                print(response_text)
                return response_text
            return response_text
        else:
            if self.language == 'tr':
                return "Rasa cevap veremedi."
            elif self.language == 'en':
                return "No response from Rasa"

class GTTSConverter:
    def __init__(self):
        self.language_code = 'en'

    def set_language(self, language):
        if language == 'tr':
            self.language_code = 'tr'
        elif language == 'en':
            self.language_code = 'en'

    def text_to_speech(self, text):
        tts = gTTS(text=text, lang=self.language_code)
        audio_file = BytesIO()
        tts.write_to_fp(audio_file)
        audio_file.seek(0)
        return audio_file

class AudioPlayer:
    def __init__(self):
        pass

    def play_audio(self, audio_file):
        sound = AudioSegment.from_file(audio_file, format='mp3')
        sound.export("response.wav", format="wav")
        play(sound)
class App:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.window = QWidget()
        self.window.setWindowTitle("UPF Assistant")

        #Define language
        self.language = "english"

        # Create a QLabel with the welcome message
        self.welcome_label = QLabel("Welcome to the UPF Assistant!")
        self.welcome_label.setAlignment(Qt.AlignCenter)
        self.welcome_label.setStyleSheet("font-size: 18pt;")

        # Create the logo and button
        self.logo_label = QLabel()
        self.logo_pixmap = QPixmap("logo.png")
        self.logo_label.setPixmap(self.logo_pixmap)
        self.record_button = QPushButton("TAP TO TALK")
        self.record_button.clicked.connect(self.record_and_transcribe_audio)
        self.record_button.setStyleSheet(
            "background-color:#001f3f; color:#ffffff; font-size: 14pt; border-radius: 50%;")
        self.record_button.setFixedSize(239, 100)

        # Create a QLabel to display the response text
        self.response_label = QLabel("")
        self.response_label.setAlignment(Qt.AlignCenter)
        self.response_label.setStyleSheet("font-size: 14pt;")
        #select language
        self.language_switch = QComboBox()
        self.language_switch.addItems(['English', 'Turkish'])
        self.language_switch.currentIndexChanged.connect(self.set_language)

        # Create a GTTSConverter object
        self.gtts_converter = GTTSConverter()
        self.rasa_connector = RasaConnector()
        # Create a layout and add the logo, welcome label, record button, and response label
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.logo_label)
        self.layout.addWidget(self.welcome_label)
        self.layout.addWidget(self.record_button)
        self.layout.addWidget(self.response_label)
        self.layout.addWidget(self.language_switch)
        self.layout.setAlignment(Qt.AlignCenter)
        self.layout.addStretch()

        # Set the layout for the window and show it
        self.window.setLayout(self.layout)
        self.window.setStyleSheet("background-color:#ffffff;")
        self.window.setGeometry(400, 400, 1000, 600)
        self.window.show()

    def set_language(self, index):
        self.language = self.language_switch.itemText(index).lower()


    def record_and_transcribe_audio(self):
        recorder = AudioRecorder()
        # Record audio and save it to a file
        audio_file_path = recorder.record_audio()
        transcriber = WhisperTranscriber()
        # Transcribe the audio file
        if self.language == 'english':
            text = transcriber.transcribe_eng(audio_file_path)
        elif self.language == 'turkish':
            text = transcriber.transcribe_tur(audio_file_path)
            text = translate(text,'en','tr')
        rasa_connector = RasaConnector()
        if self.language == 'english':
            self.rasa_connector.set_language('en')
        elif self.language == 'turkish':
            self.rasa_connector.set_language('tr')
        # Send the transcribed text to Rasa with the language parameter and get the response text
        response_text = rasa_connector.send_message(text)
        if self.language=='turkish':
            response_text = translate(response_text,'tr','en')
        # Set the response label text to the response text
        print(response_text)
        #self.response_label.setText(response_text)
        # Convert the response to speech
        if self.language == 'english':
            self.gtts_converter.set_language('en')
        elif self.language == 'turkish':
            self.gtts_converter.set_language('tr')

        speech_file = self.gtts_converter.text_to_speech(response_text)
        player = AudioPlayer()
        # Play the speech
        player.play_audio(speech_file)

    def run(self):
        sys.exit(self.app.exec_())

app = App()
app.run()
