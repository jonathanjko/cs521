"""
Jonathan Ko
Class API_Handler
API_Handler class to handle API calls to Spotify to retrieve authentication
token, to hold client_id and client_secret. API handler also retrieves
information regarding the artist and top 10 songs. API handler will search
the Spotify database for the artist.
"""
import re
import datetime
import os
import base64
import json
from requests import post,get
import copy
import logging
import random
import spotipy

from spotipy.oauth2 import SpotifyOAuth
from flask import session, request, redirect, url_for
import logging
import time


class APIHandler:
    def __init__(self, client_ID, client_secret, redirect_uri):
        self.client_ID = client_ID
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.token = None
        self.token_expires = datetime.datetime.now()
        self.data = {"grant_type": "client_credentials"}
        self.token_valid = False
        self.sp_oauth = None
        self.spotipy_instance = None
        self.token_info = None  # Ensure token_info is initialized to None
        
    
    def create_spotify_oauth(self):
        self.sp_oauth = SpotifyOAuth(
            client_id=self.client_ID,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            scope="user-read-playback-state user-read-currently-playing user-modify-playback-state"
        )
        return self.sp_oauth
    
    def get_access_token(self, code):
        """Retrieve access token from Spotify using the OAuth code."""
        try:
            token_info = self.sp_oauth.get_access_token(code)
            self.set_token_info(token_info)  # Store the token info
            return token_info
        except Exception as e:
            raise Exception(f"Error retrieving access token: {str(e)}")
            

    def get_spotify_instance(self):
        """Retrieve a Spotify instance with a valid token."""
        token_info = session.get("token_info", None)
        if not token_info:
            raise Exception("Token information is missing.")
        
        # Step 4: Check if token has necessary scopes
        scopes = token_info.get('scope', '')
        if 'user-read-playback-state' not in scopes or 'user-read-currently-playing' not in scopes:
            logging.error("Token does not have the required scopes.")
            raise Exception("Token does not have the required scopes.")
        
        # Ensure token is refreshed if necessary
        self.refresh_token_if_needed()
        return self.spotipy_instance
    
    def set_token_info(self, token_info):
        self.token_info = token_info  # Set token info from Flask route
        
    def get_token_info(self):
        return self.token_info  # Retrieve token info when needed
    

    def refresh_token_if_needed(self):
        """Refresh the token if it has expired."""
        token_info = session.get("token_info", None)
        if not token_info:
            raise Exception("Token information is missing.")
        
        now = datetime.datetime.now().timestamp()
        is_token_expired = token_info['expires_at'] - now < 60

        if is_token_expired:
            logging.info("Token expired. Refreshing token...")
            token_info = self.sp_oauth.refresh_access_token(token_info['refresh_token'])
            session['token_info'] = token_info
        
        self.spotipy_instance = spotipy.Spotify(auth=token_info['access_token'])


    
    def get_token(self):
        """
        Request a new token from Spotify API if the current token is expired or invalid.
        """
        
        token_info = session.get("token_info", None)
        if not token_info:
            raise Exception("Token information is missing.")
            
        if self.token and datetime.datetime.now() < self.token_expires:
            return self.token  # Return existing token if it's still valid

        url = "https://accounts.spotify.com/api/token"
        if not self.client_ID or not self.client_secret:
            raise ValueError("Client ID and client secret must be set.")

        auth_string = f"{self.client_ID}:{self.client_secret}"
        auth_bytes = auth_string.encode("utf-8")
        auth_base64 = base64.b64encode(auth_bytes).decode("utf-8")

        headers = {
            "Authorization": "Basic " + auth_base64,
            "Content-Type": "application/x-www-form-urlencoded"
        }

        response = post(url, headers=headers, data=self.data)

        if response.status_code != 200:
            logging.error(f"Failed to get token: {response.status_code} - {response.text}")
            raise Exception("Failed to authenticate with Spotify API.")

        json_result = response.json()
        self.token = json_result["access_token"]
        expires_in = json_result["expires_in"]  # Time in seconds until the token expires
        self.token_expires = datetime.datetime.now() + datetime.timedelta(seconds=expires_in)
        self.token_valid = True

        return self.token

    def _get_auth_header(self):
        """Return the authorization headers using the access token."""
        if not self.token_info:
            raise ValueError("No token_info available. Please authenticate first.")
        access_token = self.token_info['access_token']
        return {"Authorization": f"Bearer {access_token}"}
    
    def is_token_expired(self):
        """Check if the token has expired."""
        return self.sp_oauth.is_token_expired(self.token_info)

    #searching for artist in spotify library returns a 
    def search_for_artist(self,artist_name):
        """
        Search for an artist by name in Spotify's library.
        Returns the first matching artist's data or None if not found.
        """
        url = "https://api.spotify.com/v1/search"
        headers = self._get_auth_header()
        query = f"?q={artist_name}&type=artist&limit=1"

        response = get(url + query, headers=headers)

        if response.status_code != 200:
            logging.error(f"Failed to search for artist: {response.status_code} - {response.text}")
            return None

        artists = response.json().get("artists", {}).get("items", [])
        if not artists:
            print(f"No artist found for name: {artist_name}")
            return None

        return artists[0]
    

    def get_songs_by_artist(self,artist_id):
        """
        Get the top tracks for a given artist by their Spotify artist ID.
        Returns a list of tracks.
        """
        url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
        headers = self._get_auth_header()

        response = get(url, headers=headers)

        if response.status_code != 200:
            logging.error(f"Failed to get songs for artist: {response.status_code} - {response.text}")
            return []

        tracks = response.json().get("tracks", [])
        return tracks

    #Common problems with access token expiring, function to determine validitiy
    def isgoodtoken(self,token_expires,valid_request):
        """Check if the current token is valid and hasn't expired."""
        if self.token_valid and datetime.datetime.now() < self.token_expires:
            print("Token is valid and active.")
            return True
        else:
            print("Token is invalid or expired.")
            return False
        
    def get_user_queue(self):
        """Fetch the user's current queue."""
        url = "https://api.spotify.com/v1/me/player/queue"
        headers = self._get_auth_header()
        response = get(url, headers=headers)

        if response.status_code != 200:
            logging.error(f"Failed to get user queue: {response.status_code} - {response.text}")
            return None
        
        return response.json()
    
    def randomize_queue(queue):
        """Randomize the order of tracks in the queue."""
        tracks = queue['queue']  # Assuming 'queue' is a list of tracks in the response JSON
        random.shuffle(tracks)
        return tracks
    
    def add_to_queue(self, track_uri):
        """Add a track to the user's queue."""
        url = f"https://api.spotify.com/v1/me/player/queue?uri={track_uri}"
        headers = self.__api_handler._get_auth_header()
        response = post(url, headers=headers)
        
        if response.status_code == 204:
            logging.info(f"Successfully added track to queue: {track_uri}")
            return True
        else:
            logging.error(f"Failed to add track to queue: {response.status_code} - {response.text}")
            return False
    
    def skip_to_next_track(self):
        """Skip to the next track in the user's playback."""
        url = "https://api.spotify.com/v1/me/player/next"
        headers = self._get_auth_header()
        response = post(url, headers=headers)
        
        if response.status_code != 204:
            logging.error(f"Failed to skip to next track: {response.status_code}")
            return False
        
        return True
    
    
    def check_active_device(self):
        """Check if there's an active device for playback."""
        url = "https://api.spotify.com/v1/me/player"
        headers = self.__api_handler._get_auth_header()
        response = get(url, headers=headers)
        
        if response.status_code == 200:
            player_info = response.json()
            if player_info.get("device"):
                return True
        return False
