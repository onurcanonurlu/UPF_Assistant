import pandas as pd
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import requests


class GetProfessorInfoAction(Action):
    def name(self):
        return "action_get_professor_info"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        # Load data
        df = pd.read_csv("professors.csv")

        ###
        print(tracker.latest_message['intent'].get('name') )
        ###
        # Get professor's name entity
        professor_name = next(tracker.get_latest_entity_values("professor_name"), None)

        # Get room and group entities
        room = next(tracker.get_latest_entity_values("room"), None)
        group = next(tracker.get_latest_entity_values("group"), None)

        if professor_name is None and room is None and group is None:
            dispatcher.utter_message(response="utter_no_professor_name_or_room_or_group")
            return []

        if room is not None:
            matching_professors = df[df["room"] == room]

            if matching_professors.empty:
                dispatcher.utter_message(response="utter_no_professor_found_in_room")
                return []

            professors_list = matching_professors["name"].tolist()
            response = "The following professors are in that room: {}".format(", ".join(professors_list))
            dispatcher.utter_message(text=response)

        elif group is not None:
            matching_professors = df[df["group"].str.contains(group, case=False)]


            if matching_professors.empty:
                dispatcher.utter_message(response="utter_no_professor_found_in_group")
                return []

            professors_list = matching_professors["name"].tolist()
            response = "The following professors are in that group: {}".format(", ".join(professors_list))
            dispatcher.utter_message(text=response)


        else:
            # Split professor name entity into separate words, if it has more than 1 word
            professor_name_words = professor_name.split() if len(professor_name.split()) > 1 else [professor_name]

            # Find matching professor in dataframe
            max_matches = 0
            matching_professor = None
            for i, row in df.iterrows():
                num_matches = 0
                for name_word in professor_name_words:
                    if name_word.lower() in row['name'].lower():
                        num_matches += 1
                if num_matches > max_matches:
                    max_matches = num_matches
                    matching_professor = row

            if matching_professor is None:
                dispatcher.utter_message(response="utter_no_professor_found")
            else:
                # Check which intent was triggered by the user and respond accordingly
                intent = tracker.latest_message['intent'].get('name')
                if intent == "get_professor_group":
                    response = f"Professor {matching_professor['name']} is in {matching_professor['group']} group."
                elif intent == "get_professor_room":
                    response = f"Professor {matching_professor['name']} is located in {matching_professor['room']}."
                    if not pd.isna(matching_professor['building']):
                        response += f" The room is in the {matching_professor['building']} building."
                else:
                    response = f"Professor {matching_professor['name']} is a professor at UPF. They are in {matching_professor['group']} group. Their office is {matching_professor['room']}"
                    if not pd.isna(matching_professor['building']):
                        response += f" in the {matching_professor['building']} building."
                    else:
                        response += "."

                dispatcher.utter_message(text=response)

        return []

class GetWeatherAction(Action):
    def name(self):
        return "action_get_weather"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        ###
        tracker.latest_message['intent'].get('name')
        ###
        url = "https://api.openweathermap.org/data/2.5/weather?lat=41.390205&lon=2.154007&appid=0e2d35e359e3aa28d7b493c9ee4a19f2"
        response_weather = requests.get(url)
        weather_descp = response_weather.json()['weather'][0]['main']
        weather_degree = float(response_weather.json()['main']['temp'] - 272.15)
        weather_degree = "{:.1f}".format(weather_degree)
        weather_message = f"The weather in Barcelona is currently {weather_descp} with a temperature of {weather_degree} degrees."
        dispatcher.utter_message(text=weather_message)

        return []