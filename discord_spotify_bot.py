import discord
from discord.ext import commands
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import re
import yt_dlp as youtube_dl

# Spotify API credentials
SPOTIPY_CLIENT_ID = 'Client ID from Spotify Dev'
SPOTIPY_CLIENT_SECRET = 'Client Secret from Spotify Dev'
SPOTIPY_REDIRECT_URI = 'http://localhost:8888/callback'
SPOTIFY_PLAYLIST_ID = 'Spotify Playlist ID' # Example: if playlist link is https://open.spotify.com/playlist/test?si=example, then "test" is the playlist ID

# Discord Bot Token
DISCORD_TOKEN = 'Discord bot access token'

# Initialize Spotify client
sp = None
try:
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=SPOTIPY_REDIRECT_URI,
        scope="playlist-modify-public"))
    print("Spotify client initialized successfully.")
except Exception as e:
    print(f"Failed to initialize Spotify client: {e}")

# Set up Discord bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

def get_youtube_info(url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'extract_flat': True,
        'force_generic_extractor': True,
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        video_title = info_dict.get('title', None)
        uploader = info_dict.get('uploader', None)
    return video_title, uploader

def clean_up_artist_name(artist_name, exclusions=None):
    if not exclusions:
        exclusions = ["*topic*", "*vevo*", "*official*", "*online*", "*band*", "*video*", "*lyric*", "*visualizer*"]
    
    # Convert wildcard patterns to regex patterns
    patterns = [re.escape(word).replace(r'\*', '.*') for word in exclusions]
    
    # Create a regex that will match any of the exclusion patterns
    regex = re.compile(r'\b(?:' + '|'.join(patterns) + r')\b', re.IGNORECASE)
    
    # Substitute the matched patterns with an empty string
    cleaned_name = regex.sub("", artist_name).strip()
    
    # Debugging: Log the cleaned artist name
    print(f"Cleaned artist name: '{cleaned_name}' (from '{artist_name}')")
    
    return cleaned_name

def search_spotify_dynamic(track_name, uploader_name):
    uploader_cleaned = clean_up_artist_name(uploader_name)
    # Perform a search with the uploader's cleaned name
    query = f"{track_name} {uploader_cleaned}"
    result = sp.search(q=query, type='track')
    
    if result['tracks']['items']:
        track = result['tracks']['items'][0]
        track_uri = track['uri']
        track_name = track['name']
        artist_name = track['artists'][0]['name']  # Assume the first artist is the main one
        sp.playlist_add_items(SPOTIFY_PLAYLIST_ID, [track_uri])
        return track_name, artist_name, track['external_urls']['spotify']
    
    # Fallback: Search only by track name
    query = track_name
    result = sp.search(q=query, type='track')
    
    if result['tracks']['items']:
        track = result['tracks']['items'][0]
        track_uri = track['uri']
        track_name = track['name']
        artist_name = track['artists'][0]['name']
        sp.playlist_add_items(SPOTIFY_PLAYLIST_ID, [track_uri])
        return track_name, artist_name, track['external_urls']['spotify']
    
    return None, None, None

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # YouTube links
    youtube_url_pattern = re.compile(r'https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+')
    match_youtube = youtube_url_pattern.search(message.content)
    if match_youtube:
        youtube_url = match_youtube.group(0)
        video_title, uploader = get_youtube_info(youtube_url)

        print(f"Extracted video title: {video_title}")
        print(f"Extracted uploader: {uploader}")

        if uploader and video_title:
            track_name, artist_name, spotify_url = search_spotify_dynamic(video_title.strip(), uploader.strip())
            if spotify_url:
                # Fetch the YouTube video thumbnail
                ydl_opts = {'quiet': True, 'skip_download': True}
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    info_dict = ydl.extract_info(youtube_url, download=False)
                    thumbnail_url = info_dict.get('thumbnail')

                # Create the embed message
                embed = discord.Embed(
                    title=f"{track_name}",
                    description=f"by {artist_name}",
                    url=spotify_url,
                    color=discord.Color.green()
                )
                embed.set_thumbnail(url=thumbnail_url)
                embed.add_field(name="Added to Playlist", value="Success!", inline=True)
                embed.set_footer(text="Converted from YouTube")

                await message.channel.send(embed=embed)
            else:
                await message.channel.send(f"Could not find a matching Spotify track for '{video_title}' by '{uploader}'.")
        else:
            await message.channel.send("Could not extract or parse track and artist info from the YouTube title or uploader.")

    # Spotify links
    spotify_url_pattern = re.compile(r'https?://open\.spotify\.com/track/([a-zA-Z0-9]+)')
    match_spotify = spotify_url_pattern.search(message.content)
    if match_spotify:
        spotify_track_id = match_spotify.group(1)
        track_info = sp.track(spotify_track_id)  # Fetch track info from Spotify
        track_name = track_info['name']
        artist_name = track_info['artists'][0]['name']  # Assuming the first artist is the main one
        track_uri = track_info['uri']
        album_art_url = track_info['album']['images'][0]['url']  # Fetch album art

        # Add the track to the playlist
        sp.playlist_add_items(SPOTIFY_PLAYLIST_ID, [track_uri])

        # Create the embed message
        embed = discord.Embed(
            title=f"{track_name}",
            description=f"by {artist_name}",
            url=match_spotify.group(0),
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=album_art_url)
        embed.add_field(name="Added to Playlist", value="Success!", inline=True)
        embed.set_footer(text="Powered by Spotify")

        await message.channel.send(embed=embed)

# Run the bot
bot.run(DISCORD_TOKEN)