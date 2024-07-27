from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from decouple import config, Csv
import os
import json

# Define SCOPES required for Google Calendar and Meet APIs
SCOPES = [
    "https://www.googleapis.com/auth/meetings.space.created",
    "https://www.googleapis.com/auth/calendar.events",
]


def save_credentials(creds):
    """Save the refreshed credentials to a secure storage"""
    with open("token.json", "w") as token_file:
        token_file.write(creds.to_json())


def load_credentials():
    """Load credentials from secure storage"""
    if os.path.exists("token.json"):
        with open("token.json", "r") as token_file:
            creds_info = json.load(token_file)
            return Credentials.from_authorized_user_info(creds_info, SCOPES)
    return None


def get_authorized_credentials():
    creds = load_credentials()
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Failed to refresh token: {e}")
                creds = None
        if not creds:
            # Reauthorize the application
            flow = InstalledAppFlow.from_client_config(
                {
                    "installed": {
                        "client_id": config("GOOGLE_CLIENT_ID"),
                        "project_id": config("GOOGLE_PROJECT_ID"),
                        "auth_uri": config("GOOGLE_AUTH_URI"),
                        "token_uri": config("GOOGLE_TOKEN_URI"),
                        "auth_provider_x509_cert_url": config(
                            "GOOGLE_AUTH_PROVIDER_CERT_URL"
                        ),
                        "client_secret": config("GOOGLE_CLIENT_SECRET"),
                        "redirect_uris": config("GOOGLE_REDIRECT_URI", cast=Csv()),
                    }
                },
                SCOPES,
            )
            creds = flow.run_local_server(port=0)
            save_credentials(creds)
    return creds


def create_meet_link():
    creds = get_authorized_credentials()
    if not creds:
        return "Failed to obtain credentials."

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
