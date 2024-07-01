from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os.path
import datetime

# Define the scopes required for accessing Google Calendar and creating events with Meet links
SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/calendar.events",
]


def main():
    """Shows basic usage of the Google Calendar API.
    Creates a Google Meet event in the user's calendar and invites attendees.
    """
    creds = None
    # Check if token.json file exists, which stores the user's access and refresh tokens
    if os.path.exists("token.json"):
        # Load the credentials from the token file
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Refresh the credentials using the refresh token
            creds.refresh(Request())
        else:
            # Prompt the user to log in and authorize the application
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        # Build the Google Calendar service
        service = build("calendar", "v3", credentials=creds)

        # Define the date and time for the event
        start_time = (
            datetime.datetime(2024, 7, 1, 18, 55, 0).isoformat() + "Z"
        )  # July 1, 2024, 6:55 PM UTC
        end_time = (
            datetime.datetime(2024, 7, 1, 19, 55, 0).isoformat() + "Z"
        )  # July 1, 2024, 7:55 PM UTC

        # Define the event details
        event = {
            "summary": "Google Meet API Test Meeting",  # Event title
            "start": {
                "dateTime": start_time,  # Start time of the event
                "timeZone": "Africa/Nairobi",  # Timezone for the start time
            },
            "end": {
                "dateTime": end_time,  # End time of the event
                "timeZone": "Africa/Nairobi",  # Timezone for the end time
            },
            "conferenceData": {
                "createRequest": {
                    "requestId": "sample123",  # Unique request ID for creating the conference
                    "conferenceSolutionKey": {
                        "type": "hangoutsMeet"
                    },  # Type of conference (Google Meet)
                }
            },
            "attendees": [
                {
                    "email": "daniel.karume@students.jkuat.ac.ke"
                },  # First attendee's email
                {"email": "danielkarumembugua@gmail.com"},  # Second attendee's email
            ],
            "reminders": {
                "useDefault": False,  # Use custom reminders instead of default
                "overrides": [
                    {
                        "method": "email",
                        "minutes": 24 * 60,
                    },  # Send email reminder 24 hours before the event
                    {
                        "method": "popup",
                        "minutes": 10,
                    },  # Show popup reminder 10 minutes before the event
                ],
            },
        }

        # Insert the event into the primary calendar
        event = (
            service.events()
            .insert(
                calendarId="primary",
                body=event,
                conferenceDataVersion=1,
                sendUpdates="all",
            )
            .execute()
        )
        # Print the Google Meet link for the created event
        print("Meeting created:", event.get("hangoutLink"))
    except Exception as error:
        # Handle errors from Google Calendar API
        print(f"An error occurred: {error}")


if __name__ == "__main__":
    main()
