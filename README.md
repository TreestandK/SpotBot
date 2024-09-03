# Instruction for SpotBot

## Step 1: Sign up for Spotify Dev account
	- Go to https://developer.spotify.com/dashboard/
	- Press Login
	- Click "Create App"
	- Create app name, app description, and set "Redirect URIs" to
		- http://localhost:8888/callback
	- Check all API/SDK
	- Check "I understand"
	- Click "Save

## Step 2: Create Discord bot
	- Go to https://discord.com/developers/
	- Create a new application
	- Go to the bot tab
	- Press "reset access token"
	- Copy token to notepad so you dont lose it
	- Check the buttons for "Message Content Intent"
	- Give bot permissions for Send Messages, Embed Links
	- Click "Installation"
	- Copy link from "Install Link" and invite to server

## Step 3: Create Spotify playlist
	- Create new Spotify playlist that will be used for channel
	- Click the 3 dots and click "Invite collaborators"
	- Use the link generated from this for the next step, this will be what the bot uses 
    to be able to add to the playlist

## Step 4: Running the bot
	- Install Python on PC
		- Go to https://www.python.org/downloads/windows/
		- Click Download Windows installer (64-bit)
		- Go through installer
	- Setup a directory on PC where bot will live
		- Example: D:\spotbot\
	- Replace needed variables
		-Open discord_spotify_bot.py in any text editor
			- Notepad, Sublime, Visual Studio Code
		- Replace the following with the correct information
			- SPOTIPY_CLIENT_ID
			- SPOTIPY_CLIENT_SECRET
			- SPOTIFY_PLAYLIST_ID
		- Save file
	- Open directory in command prompt
		- Right click in directory and click "open in terminal" 
	- In the terminal, type "pip install discord.py spotipy requests yt-dlp"
	- Run bot with "python discord_spotify_bot.py"