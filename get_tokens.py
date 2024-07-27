import requests


def get_new_access_token(client_id, client_secret, refresh_token):
    url = "https://oauth2.googleapis.com/token"

    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }

    try:
        response = requests.post(url, data=data)

        response.raise_for_status()

        token_info = response.json()
        return token_info.get("access_token")

    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
        return None
    except Exception as err:
        print(f"An error occurred: {err}")
        return None
