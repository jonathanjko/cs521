# cs521
Spotify API and Data Analysis Project
This project integrates a Flask web application that interacts with the Spotify API to manage user playlists and queues, and conducts an analysis of Spotify's top hits from 1998 to 2020 using R. 

The repository is divided into two main parts:

API-based Playlist and Queue Management (Python)
Spotify Top Hits Data Analysis (R)

Table of Contents:
Project Overview
API-based Playlist and Queue Management
Setup Instructions
Running the Flask App
Spotify Data Analysis
Running the R Script

Project Overview:
API Component: Integrates with the Spotify API, allowing users to randomize their queue and create custom playlists.
Data Analysis Component: Provides insights into Spotify's top hits from 1998-2020, identifying trends in energy, danceability, and other song attributes over time.
API-based Playlist and Queue Management
This part of the project uses Python's Flask web framework to interact with the Spotify API. Users can authenticate with their Spotify account, randomize their queue, or create playlists based on selected artists.

Setup Instructions
Clone the Repository:

git clone https://github.com/yourusername/Spotify_Analysis_and_API_Project.git
cd Spotify_Analysis_and_API_Project/api
Install Dependencies: Ensure you have Python 3.x installed, then install the required packages:
pip install -r requirements.txt
Set up Spotify Credentials: Create an environment_variables.txt file with your Spotify API credentials (client_id and client_secret).

Run the Flask Application:
python main.py
Running the Flask App
Navigate to http://localhost:5001/authorize to authenticate with Spotify.
Once authenticated, follow the instructions in the terminal to:
Randomize your queue
Create a playlist or
Retrieve existing playlists


Spotify Data Analysis
The R script performs data analysis on Spotify's top hits from 1998-2020, revealing trends and correlations between song attributes such as loudness, energy, and danceability.

Running the R Script
Navigate to the analysis folder:
cd ../analysis
Run the R Script: Open the CS544_Final_Project_Ko.R file in an R environment (e.g., RStudio) and execute the script to generate the data analysis outputs.
