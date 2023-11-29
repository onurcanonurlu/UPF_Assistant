import whisper
import requests
import json
audio= "/Users/onurcan/Documents/q1.m4a"
model = whisper.load_model("base")
result = model.transcribe(audio)
text = result["text"]

# Define the Rasa endpoint
url = "http://localhost:5005/webhooks/rest/webhook"

# Define the data to be sent as a POST request to Rasa
data = {
    "sender": "test_user",
    "message": text,
    "metadata": {}
}

# Send the POST request to Rasa
response = requests.post(url, json=data)
# Get the response text as a string
response_text = response.text
# Parse the response string to a Python object
response_data = json.loads(response_text)

# Print the text from the response
print(response_data[0]['text'])