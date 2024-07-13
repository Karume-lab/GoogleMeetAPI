from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os
from datetime import datetime, timedelta

SCOPES = [
    "https://www.googleapis.com/auth/meetings.space.created",
    "https://www.googleapis.com/auth/calendar.events",
]


def create_open_meet_link(appointment):
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        meet_service = build("meet", "v2", credentials=creds)

        # Create a new space
        space = meet_service.spaces().create().execute()

        # Update the space to have open access
        update_body = {"config": {"accessType": "OPEN", "entryPointAccess": "ALL"}}
        updated_space = (
            meet_service.spaces()
            .patch(
                name=space["name"],
                updateMask="config.accessType,config.entryPointAccess",
                body=update_body,
            )
            .execute()
        )

        meeting_link = updated_space["meetingUri"]

        return f"Meeting link: {meeting_link}"

    except Exception as e:
        return f"An error occurred: {e}"


if __name__ == "__main__":
    result = create_open_meet_link()
    print(result)
