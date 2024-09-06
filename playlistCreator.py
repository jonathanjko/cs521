"""
Jonathan Ko
PlaylistCreator
"""
import random
import os
import logging
# Configure logging
logging.basicConfig(filename='playlist_creator.log', level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')
import sys
sys.path.append('/Users/jonathanko/Documents/School/CS521/API Playlist')
from API_Handler import APIHandler
#class to handle generating the playlist and randomizing the playlist checking if there are duplicates

class playlistCreator:
    def __init__(self, api_handler):
        self.master_playlist = {}
        self.__api_handler = api_handler
        
        
    def artist_to_tuples(self,artist_name):
        """Convert artist's songs into tuples of (song_name, artist_name)."""
        try:
            artist_response = self.__api_handler.search_for_artist(artist_name)
            if not artist_response:
                logging.error(f"Artist '{artist_name}' not found.")
                return []
            artist_id = artist_response["id"]
            songs = self.__api_handler.get_songs_by_artist(artist_id)
            return [(song['name'], song["artists"][0]['name']) for song in songs]
        except KeyError as e:
           logging.error(f"KeyError when processing artist '{artist_name}': {e}")
           return []
        except Exception as e:
           logging.error(f"Unexpected error in artist_to_tuples for '{artist_name}': {e}")
           return []

        
    def create_playlist(self,playlist_name,artist_names):
        """Create a playlist from a list of artist names."""
        if not self.validate_artist_names(artist_names):
           return None
       
        ind_playlist = []
        for artist_name in artist_names:
           artist_songs = self.artist_to_tuples(artist_name)
           if artist_songs:
               random_song_artist = self.select_random_song(artist_songs)
               ind_playlist.append(random_song_artist)
        
        if ind_playlist:
           self.master_playlist[playlist_name] = ind_playlist
           print(f"Your generated playlist: {playlist_name} \nSongs and Artists:  {ind_playlist}")
           return self.master_playlist[playlist_name]
        else:
           logging.error("Failed to create playlist due to missing song data.")
           return None
        

    def select_random_song(self, song_list):
        """Select a random song from a list."""
        try:
            return random.choice(song_list)
        except IndexError as e:
            logging.error(f"IndexError in select_random_song: {e}")
            return None
    
    def get_playlist(self,playlist_name):
        """Retrieve a playlist by name."""
        try:
            return self.master_playlist[playlist_name]
        except KeyError:
            logging.error(f"Playlist '{playlist_name}' not found.")
            return None

    def validate_artist_names(self, artist_names):
        """Validate that the user has provided exactly 5 artist names."""
        if len(artist_names) != 5:
            print("Please enter exactly 5 artists.")
            logging.error(f"Invalid number of artists provided: {len(artist_names)}. Expected 5.")
            return False
        if any(not name.strip() for name in artist_names):
            print("Artist names cannot be empty.")
            logging.error("One or more artist names were empty.")
            return False
        return True
    
    def get_all_playlists_summary(self):
        """Return a string summary of all playlists stored in the master_playlist."""
        if not self.master_playlist:
            return "No playlists have been created yet."
        
        summary = ["Created Playlists:"]
        for idx, playlist_name in enumerate(self.master_playlist.keys(), start=1):
            summary.append(f"{idx}. {playlist_name}")
            for song_idx, (song_name, artist_name) in enumerate(self.master_playlist[playlist_name], start=1):
                summary.append(f"   {song_idx}. {song_name} by {artist_name}")
        return "\n".join(summary)

    def view_all_playlists(self):
        """View all playlists stored in the master_playlist."""
        print(self.get_all_playlists_summary())
        
    def test_method(self):
        """Simple method to test if new methods are recognized."""
        print("Test method is working.")
            
    def __repr__(self):
        """Provide a string representation of all playlists."""
        repr_string = ""
        for idx, name_playlist in enumerate(self.master_playlist.keys()):
            repr_string += f"{idx + 1}. {name_playlist}\n"
            for ind, artist_songs in enumerate(self.master_playlist[name_playlist]):
                repr_string += f"   {ind + 1}. {artist_songs}\n"
        return repr_string
                
    def __eq__(self,other):
        """Compare two PlaylistCreator objects."""
        if not isinstance(other, playlistCreator):
            return NotImplemented
        return self.master_playlist == other.master_playlist
    
    