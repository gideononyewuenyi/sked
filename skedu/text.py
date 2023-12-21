# # Import the function at the beginning of your test script
from views import extract_appointment_time

# # Sample user input
# sample_input = "Set up an appointment for 3:00 PM"

# # Call the function with the sample input
# response = process_input_with_openai(sample_input)

# # Print or assert the response to check if it's as expected
# print(response)



# # Import the function at the beginning of your test script
# from views import setup_google_calendar_api

# # Call the function to set up the Google Calendar API
# service = setup_google_calendar_api()

# # Check if the service object is not None
# if service:
#     print("Google Calendar API setup successful")
# else:
#     print("Google Calendar API setup failed")



test_cases = [
    "Set up an appointment for 12:00 PM on 20th December",
    "How about next Friday morning for the meeting?",
    # ... more test cases
]

for case in test_cases:
    print(f"Input: {case}")
    extracted_time = extract_appointment_time(case)
    print(f"Extracted Time: {extracted_time}")
