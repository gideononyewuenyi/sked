from django.shortcuts import render
from django.http import JsonResponse
from dateutil import parser
import json
from django.views.decorators.csrf import csrf_exempt
import requests
import os
from dotenv import load_dotenv
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import timedelta
import re  
import dateutil.parser as date_parser  
import spacy
nlp = spacy.load("en_core_web_sm")

load_dotenv()  

GPT_API_KEY = os.getenv('GPT_API_KEY')

# Utility function to process input with OpenAI
def process_input_with_openai(user_input):
    api_key = os.getenv("GPT_API_KEY")
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    payload = {
        'max_tokens': 50,  
        'model': 'gpt-4', 
        'messages': [{"role": "user", "content": user_input}]
    }
    response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=payload)

    # Extract the processed input from the response
    processed_input = response.json()["choices"][0]["message"]["content"]
    return user_input + processed_input  

# Utility function to set up Google Calendar API
def setup_google_calendar_api():
    try:
        # Loading credentials from the token file
        creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/calendar'])

        # Creating a Google Calendar API service
        service = build('calendar', 'v3', credentials=creds)
        return service
    except Exception as e:
        raise RuntimeError(f"Google Calendar API error: {str(e)}")


# Function to find an existing event with the same start time
def find_existing_event(service, start_time):
    events = service.events().list(calendarId='primary', timeMin=start_time.isoformat(), singleEvents=True).execute()
    for event in events.get('items', []):
        # Comparing the start time of the event with the given start_time
        if event.get('start', {}).get('dateTime') == start_time.isoformat():
            return event['id']
    return None  # To Return None if no matching event is found

# Function to extract appointment time from processed text
def extract_appointment_time(user_input):
    try:
        # Processing user input with spaCy
        doc = nlp(user_input)

        # Extracting time entities from spaCy's parsed result
        time_entities = [ent.text for ent in doc.ents if ent.label_ == "TIME"]


        if time_entities:
            # Selecting the first time entity 
            time_str = time_entities[0]

            # Parsing the time string into a datetime object
            appointment_time = date_parser.parse(time_str, fuzzy=True)

            return appointment_time
        else:
            return None  # No time entity found in user input

    except Exception as e:
        return None  # Error occurred while extracting time


@csrf_exempt
def schedule_appointment(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid request method"}, status=400)

    try:
        data = json.loads(request.body.decode('utf-8'))
        user_input = data.get('message')
        if not user_input:
            return JsonResponse({"error": "No input provided"}, status=400)

        # Extracting the appointment date and time from the user input
        appointment_time = extract_appointment_time(user_input)

        if appointment_time:
            # Creating a Google Calendar API service
            service = setup_google_calendar_api()

            # Define the event details
            event = {
                'summary': 'Scheduled Appointment',
                'start': {
                    'dateTime': appointment_time.isoformat(),
                    'timeZone': 'Africa/Lagos',  
                },
                'end': {
                    'dateTime': (appointment_time + timedelta(hours=1)).isoformat(),
                    'timeZone': 'Africa/Lagos',  
                },
            }

            # Create a new event
            service.events().insert(calendarId='primary', body=event).execute()
            response_message = "Appointment scheduled successfully"

            return JsonResponse({"message": response_message})
        else:
            return JsonResponse({"error": "Appointment time not found in user input"}, status=400)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


