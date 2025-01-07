from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import requests

load_dotenv() 


app = FastAPI()

app.mount("/static", StaticFiles(directory="frontend"), name="static")

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")


@app.get("/")
def serve_index():
    return FileResponse("frontend/index.html")

@app.get("/login")
def login():
    """
    Direct user to Spotify's Authorization page and begin the login process.
    """
    
    scopes = "user-top-read user-read-recently-played"

    spotify_auth_url = (
        "https://accounts.spotify.com/authorize"
        f"?client_id={CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope={scopes}"
    )
    return RedirectResponse(url=spotify_auth_url)
@app.get("/dashboard")
def dashboard_page():
    return FileResponse("frontend/dashboard.html")



@app.get("/spotify/callback")
def spotify_callback(code: str):
    token_url = "https://accounts.spotify.com/api/token"
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }

    response = requests.post(token_url, data=payload)
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to get token from Spotify")

    token_data = response.json()
    access_token = token_data["access_token"]
    refresh_token = token_data.get("refresh_token", None)

    print(f"Access Token: {access_token}, Refresh Token: {refresh_token}")

    user_info_url = "https://api.spotify.com/v1/me"
    headers = {"Authorization": f"Bearer {access_token}"}
    user_info_response = requests.get(user_info_url, headers=headers)
    user_info = user_info_response.json()

    display_name = user_info.get("display_name", "User")
    return RedirectResponse(f"/dashboard?access_token={access_token}&display_name={display_name}")




class RecommendationRequest(BaseModel):
    seed_artists: list[str] = []
    seed_tracks: list[str] = []
    seed_genres: list[str] = []

@app.get("/recommendations")
def get_recommendations(token: str, refresh_token: str = None):
    """
    Fetch recommended songs based on the user's top tracks.
    """
    headers = {"Authorization": f"Bearer {token}"}
    try:
        top_tracks_url = "https://api.spotify.com/v1/me/top/tracks"
        response = requests.get(top_tracks_url, headers=headers)
        if response.status_code == 401 and refresh_token:
            print("Token expired. Refreshing token...")
            new_token = refresh_access_token(refresh_token)
            if not new_token:
                raise HTTPException(status_code=401, detail="Failed to refresh token")
            headers["Authorization"] = f"Bearer {new_token}"
            response = requests.get(top_tracks_url, headers=headers)
        response.raise_for_status()

        top_tracks_data = response.json()
        track_ids = [track["id"] for track in top_tracks_data.get("items", [])[:5]]

        params = {"limit": 10, "seed_tracks": ",".join(track_ids)} if track_ids else {"limit": 10, "seed_genres": "pop"}
        recommendations_url = "https://api.spotify.com/v1/recommendations"
        rec_response = requests.get(recommendations_url, headers=headers, params=params)
        rec_response.raise_for_status()

        return rec_response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching recommendations: {e}")

def refresh_access_token(refresh_token: str):
    token_url = "https://accounts.spotify.com/api/token"
    payload = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    response = requests.post(token_url, data=payload)
    if response.status_code != 200:
        print(f"Failed to refresh token: {response.text}")
        return None
    return response.json().get("access_token")
