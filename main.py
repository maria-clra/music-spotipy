import os
from dotenv import load_dotenv 
load_dotenv("x.env")
from flask import Flask, session, redirect, url_for, request
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)

client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
redirect_uri = 'http://127.0.0.1:8888/callback'
scope = 'playlist-read-private'

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=scope,
        show_dialog=True
    )

@app.route('/')
def home():
    if not session.get('token_info'):
        return redirect(url_for('login'))
    return redirect(url_for('get_playlists'))

@app.route('/login')
def login():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session['token_info'] = token_info
    return redirect(url_for('get_playlists'))

@app.route('/get_playlists')
def get_playlists():
    token_info = session.get('token_info')
    if not token_info:
        return redirect(url_for('login'))

    sp = Spotify(auth=token_info['access_token'])
    playlists = sp.current_user_playlists()

    playlists_html = '<h2>Suas playlists 🎶</h2><br>'
    for pl in playlists['items']:
        playlists_html += f'{pl["name"]}: <a href="{pl["external_urls"]["spotify"]}" target="_blank">{pl["external_urls"]["spotify"]}</a><br>'
    return playlists_html

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)