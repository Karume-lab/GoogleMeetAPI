from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
from decouple import config, Csv

# Define SCOPES required for Google Calendar and Meet APIs
SCOPES = [
    "https://www.googleapis.com/auth/meetings.space.created",
    "https://www.googleapis.com/auth/calendar.events",
]


def create_meet_link():
    # Construct the client_config dictionary from decouple
    client_config = {
        "installed": {
            "client_id": config("GOOGLE_CLIENT_ID"),
            "project_id": config("GOOGLE_PROJECT_ID"),
            "auth_uri": config("GOOGLE_AUTH_URI"),
            "token_uri": config("GOOGLE_TOKEN_URI"),
            "auth_provider_x509_cert_url": config("GOOGLE_AUTH_PROVIDER_CERT_URL"),
            "client_secret": config("GOOGLE_CLIENT_SECRET"),
            "redirect_uris": config("GOOGLE_REDIRECT_URI", cast=Csv()),
        }
    }

    # Hardcoded credentials
    creds = Credentials(
        token=config("GOOGLE_ACCESS_TOKEN"),
        refresh_token=config("GOOGLE_REFRESH_TOKEN"),
        token_uri=client_config["installed"]["token_uri"],
        client_id=client_config["installed"]["client_id"],
        client_secret=client_config["installed"]["client_secret"],
        scopes=SCOPES,
    )

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())

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
    result = create_meet_link()
    print(result)
