"""
Jonathan Ko
Final Project
Main File
The project is designed to compile a playlist extrapolated from spotify. Uses user
data to create an unique playlist with different artists
"""
import re
import datetime
import os.path
import string
import logging
import sys
sys.path.append('/Users/jonathanko/Documents/School/CS521/API Playlist')
from playlistCreator import playlistCreator
from API_Handler import APIHandler
from QueueManager import QueueManager
import threading  # Import the threading module
from flask import Flask, session, redirect, url_for, request
from requests import post, get
import time

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'SOMETHING-RANDOM'

# Setup logging
logging.basicConfig(filename='app.log', level=logging.ERROR)

# Global API handler variable
API = None  # Initialize as None globally

def read_environment_variables(filename):
    """Reads and returns client_id and client_secret from the environment variables file."""
    try:
        with open(filename, "r") as file:
            values = re.findall('(?:")([^"]*)', file.read(), re.U)
            client_id = values[0]
            client_secret = values[2]
            return client_id, client_secret
    except FileNotFoundError:
        logging.error("Environment variables file not found.")
        raise
    except IndexError:
        logging.error("Error parsing environment variables.")
        raise

def get_user_choice():
    """Gets the user's choice for creating or retrieving a playlist."""
    return input("Welcome to the Playlist Creator, would you like to create or get a playlist? If not, exit.\n").lower()

def create_playlist(platform):
    """Handles the creation of a new playlist."""
    playlist_name = input("Enter your playlist name: ")
    if not playlist_name:
        print("Playlist name cannot be empty.")
        return
    artists = input("Enter 5 Artists from Spotify separated by commas(,): ")
    artists_list = [artist.strip() for artist in artists.split(",")]
    if len(artists_list) != 5:
        print("Please enter exactly 5 artists.")
        return
    try:
        new_playlist = platform.create_playlist(playlist_name, artists_list)
        print(f"Playlist '{playlist_name}' created successfully!")
    except Exception as e:
        logging.error(f"Error creating playlist: {str(e)}")
        print("Failed to create the playlist. Please check the logs for more details.")

def get_playlist(platform):
    """Handles retrieving an existing playlist."""
    playlist_name = input("Enter your playlist name: ")
    if not playlist_name:
        print("Playlist name cannot be empty.")
        return

    try:
        old_playlist = platform.get_playlist(playlist_name)
        if old_playlist:
            print(f"Retrieved playlist: {old_playlist}")
        else:
            print(f"Playlist '{playlist_name}' not found.")
    except Exception as e:
        logging.error(f"Error retrieving playlist: {str(e)}")
        print("Failed to retrieve the playlist. Please check the logs for more details.")


@app.route('/')
def login():
    """Redirect the user to Spotify's OAuth login page."""
    if not API:
        logging.error("API handler not initialized.")
        return "API handler not initialized."
    
    sp_oauth = API.create_spotify_oauth()  # Use the initialized API object
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)


@app.route('/authorize')
def authorize():
    """Handle the OAuth callback from Spotify."""
    session.clear()  # Clear any previous session
    code = request.args.get('code')  # Retrieve the authorization code from Spotify's response

    # Use the API handler to get the access token using the authorization code
    token_info = API.get_access_token(code)
    
    if not token_info:
        logging.error("Authorization failed. No token_info returned.")
        return "Authorization failed. Please try again."
    
    # Save the token_info in the session or in APIHandler
    session['token_info'] = token_info
    API.token_info = token_info  # Store token_info in the API handler for further use

    logging.info("Authorization successful. Token info saved.")
    return redirect("/randomizeQueue")  # Redirect to a route that requires the token

@app.route('/randomizeQueue')
def randomize_queue():
    try:
        # Call the randomize_user_queue function up to step 3
        queue_manager.randomize_user_queue()
        return "Queue has been randomized and tracks re-added."
    except Exception as e:
        logging.error(f"Error randomizing queue: {str(e)}")
        return "An error occurred while randomizing the queue."

# @app.route('/randomizeQueue')
# def randomize_queue():
#     """Randomize the user's current Spotify queue."""
#     user_queue = queue_manager.get_user_queue()
#     if not user_queue:
#         return "Failed to retrieve the user's queue."
    
#     randomized_queue = queue_manager.randomize_queue(user_queue)
#     if not randomized_queue:
#         return "Failed to randomize the queue."
    
#     for track in randomized_queue:
#         added = queue_manager.add_to_queue(track['uri'])
#         if not added:
#             return f"Failed to add track {track['name']} to the queue."
    
#     skipped = queue_manager.skip_to_next_track()
#     if not skipped:
#         return "Failed to skip to the first track in the randomized queue."
    
#     return "Queue has been randomized and playback has been updated."

@app.route('/logout')
def logout():
    """Clear the session and log the user out."""
    session.clear()
    return redirect('/')

def run_flask_app():
    """Run the Flask app in a separate thread."""
    app.run(debug=True, use_reloader=False, port=5001)

def main():
    global API
    #clean and store environment variables into client_id and client_secret
    FILENAME = "environment_variables.txt"
    try:
        client_id, client_secret = read_environment_variables(FILENAME)
        
    except Exception as e:
        print("Failed to read environment variables. Please check the logs for more details.")
        return
    
    redirect_uri = "http://localhost:5001/authorize"
    API = APIHandler(client_id, client_secret, redirect_uri)
    
    platform = playlistCreator(API)
    global queue_manager
    queue_manager = QueueManager(API)
    
    # Start Flask app in a separate thread without making it a daemon
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.start()
    
    # Wait for authentication before proceeding
    print("App is running... Please authenticate via the /authorize route in your browser.")
    while not API.get_token_info():
        print("Please authorize the app via the /authorize route.")
        time.sleep(5)

    # Check if the user is authenticated
    if not API.get_token_info():
        print("Please authorize the app via the /authorize route.")
        return
    
    
    # Fetch and log the user's queue after initialization
    with app.app_context():  # Use Flask's app context
        user_queue = queue_manager.get_user_queue()
        if user_queue:
            logging.info(f"User's Queue: {user_queue}")
        else:
            logging.error("Failed to retrieve the user's queue.")



    # User choice loop for actions
    while True:
        try:
            print("\nChoose an action:")
            print("1. Randomize Queue")
            print("2. Create Playlist")
            print("3. Get Playlist")
            print("4. View All Playlists")
            print("5. Exit")

            choice = input("Enter your choice (1-5): ")

            if choice == '1':
                with app.app_context():
                    queue_manager.randomize_user_queue()
                print("Queue has been randomized.")
            elif choice == '2':
                create_playlist(platform)
            elif choice == '3':
                get_playlist(platform)
            elif choice == '4':
                print(platform.get_all_playlists_summary())
            elif choice == '5':
                print("Exiting. Goodbye!")
                break
            else:
                print("Invalid choice. Please select a valid option (1-5).")
        except Exception as e:
            logging.error(f"Unexpected error: {str(e)}")
            print("An unexpected error occurred. Please check the logs for more details.")

if __name__ == '__main__':
    main()