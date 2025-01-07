from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import requests

load_dotenv() 

# Initialize the FastAPI app
app = FastAPI()

app.mount("/static", StaticFiles(directory="frontend"), name="static")
# Fetch env variables
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")

# 1. Route to Start Login Flow

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


@app.get("/spotify/callback")
def spotify_callback(code: str):
    """
    Spotify redirects here after user approves the permissions.
    We exchange the received 'code' for an 'access_token' (and maybe 'refresh_token').
    """
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

    
    
    
    return RedirectResponse(f"/?access_token={access_token}&refresh_token={refresh_token}")


class RecommendationRequest(BaseModel):
    seed_artists: list[str] = []
    seed_tracks: list[str] = []
    seed_genres: list[str] = []


@app.post("/recommendations")
def get_recommendations(request_data: RecommendationRequest, token: str):
    """
    Use the Spotify Recommendations API to get recommended tracks based on the provided seeds.
    The user’s 'token' must be passed as a query parameter or in the request body.
    """
    url = "https://api.spotify.com/v1/recommendations"
    params = {
        "limit": 10,
        "seed_artists": ",".join(request_data.seed_artists),
        "seed_tracks": ",".join(request_data.seed_tracks),
        "seed_genres": ",".join(request_data.seed_genres),
    }
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch recommendations")

    return response.json()

