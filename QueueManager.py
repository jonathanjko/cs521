#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 26 14:18:47 2024

@author: jonathanko
"""

import random
import logging
from requests import get, post
from API_Handler import APIHandler
import time

class QueueManager:
    def __init__(self, api_handler):
        self.__api_handler = api_handler
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        logging.info("QueueManager initialized.")
        
    def get_user_queue(self):
        """Fetch the user's current queue."""
        logging.info("Attempting to fetch the user's current queue.")
        
        url = "https://api.spotify.com/v1/me/player/queue"
        headers = self.__api_handler._get_auth_header()
        
        response = get(url, headers=headers)
        
        if response.status_code != 200:
            logging.error(f"Failed to get user queue: {response.status_code} - {response.text}")
            return None
        
        queue_info = response.json()
        if 'queue' not in queue_info or not queue_info['queue']:
            logging.warning("The user's queue is empty or not available.")
            return None
        
        logging.info("Successfully fetched the user's queue.")
        return queue_info
        
        
    def randomize_queue(self, queue):
        try:
            # Ensure each track is a dictionary (or whatever expected format)
            for track in queue:
                if not isinstance(track, dict):
                    logging.error(f"Unexpected track structure: {track}")
                    raise ValueError("Each track should be a dictionary.")
            
            # Proceed with randomization if the tracks are correctly structured
            random.shuffle(queue)
            logging.debug(f"Queue after randomization: {queue}")
            return queue
        except Exception as e:
            logging.error(f"Error randomizing queue: {e}")
            print(f"Error randomizing queue: {e}")
            return None
    
    def add_to_queue(self, track_uri):
        """Add a track to the user's queue."""
        logging.info(f"Attempting to add track {track_uri} to the user's queue.")\
            
        # Add a short delay to ensure the queue is updated before skipping
        time.sleep(2)
        
        url = f"https://api.spotify.com/v1/me/player/queue?uri={track_uri}"
        headers = self.__api_handler._get_auth_header()
        response = post(url, headers=headers)
        
        if response.status_code != 204:
            logging.error(f"Failed to add track to queue: {response.status_code} - {response.text}")
            return False
        
        logging.info(f"Track {track_uri} added to the user's queue.")
        return True
    
    def skip_to_next_track(self):
        """Skip to the next track in the user's playback."""
        logging.info("Attempting to skip to the next track in the user's playback.")
        
        url = "https://api.spotify.com/v1/me/player/next"
        headers = self.__api_handler._get_auth_header()
        response = post(url, headers=headers)
        
        if response.status_code != 204:
            logging.error(f"Failed to skip to next track: {response.status_code} - {response.text}")
            return False
        
        logging.info("Successfully skipped to the next track.")
        return True
    
    def skip_to_track(self, track_uri):
        """Skip directly to the specified track."""
        logging.info(f"Attempting to skip to track {track_uri}.")
        
        # The Spotify API doesn't allow skipping directly to a track by URI in the queue,
        # but we can simulate skipping by adding it first and then using the skip_to_next_track method.
        self.add_to_queue(track_uri)
        return self.skip_to_next_track()
    
    
    def randomize_user_queue(self):
        """Randomize the user's current queue and start playback from the new order."""
        logging.info("Starting the process to randomize the user's queue.")

        # Step 1: Get the current queue
        current_queue = self.get_user_queue()
        if not current_queue:
            logging.error("Failed to retrieve the current queue.")
            print("Failed to retrieve the current queue.")
            return
        
        # Log the type and content of current_queue for debugging purposes
        logging.debug(f"Type of current_queue: {type(current_queue)}")
        logging.debug(f"Content of current_queue: {current_queue}")
        
        # Step 2: Access the queue's tracks from the dictionary
        if isinstance(current_queue, dict) and 'queue' in current_queue:
            queue_tracks = current_queue['queue'][:10]  # Access the list from the dictionary
        else:
            logging.error(f"Unexpected data structure in current_queue: {current_queue}")
            print(f"Error: Unexpected data structure in current_queue.")
            return

    
        if len(queue_tracks) == 0:
            logging.info("The queue is empty.")
            return
    
        logging.info(f"Found {len(queue_tracks)} tracks in the queue.")
        
        # Step 3: Randomize the limited tracks
        randomized_tracks = self.randomize_queue(queue_tracks)
        if randomized_tracks is None:
            logging.error("Queue randomization failed.")
            return
        
        # Clear the current queue (if needed) before adding the new tracks back
        logging.info("Clearing current queue (not directly supported by Spotify API, skipping).")

        # Step 4: Clear the queue (skip to each track and remove it)
        for track in queue_tracks:
            self.skip_to_next_track()

        # Step 5: Add the randomized tracks back to the queue
        for track in randomized_tracks:
            added = self.add_to_queue(track['uri'])
            if added:
                logging.info(f"Track '{track['name']}' successfully added back to the queue.")
            else:
                logging.error(f"Failed to add track: {track['name']} to the queue.")
    
        logging.info("Queue randomization process completed for the next 10 tracks.")
        print("Successfully randomized the next 10 songs in the user's queue and re-added them.")

        # Step 6: Skip to the start of the new queue (first track in the randomized queue)
        first_track_uri = randomized_tracks[0]['uri']
        if not self.skip_to_track(first_track_uri):
            logging.error("Failed to skip to the start of the new queue.")
            print("Failed to skip to the start of the new queue.")
        
        logging.info("Successfully skipped to the start of the new queue.")
        print("Successfully skipped to the start of the new queue.")
        
        
        