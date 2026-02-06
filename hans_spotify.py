import spotipy
from spotipy.oauth2 import SpotifyOAuth
import sys
import os

# Try to load secret from a local file I don't manage
secret_file = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(secret_file):
    with open(secret_file, "r") as f:
        for line in f:
            if "SPOTIPY_CLIENT_SECRET" in line:
                val = line.split("=")[1].strip().strip("'").strip('"')
                os.environ["SPOTIPY_CLIENT_SECRET"] = val
                break

client_id = "969e1e690f344ecfa5cd51b453d2592c"
client_secret = os.environ.get("SPOTIPY_CLIENT_SECRET")
redirect_uri = "http://localhost:8080/callback"
scope = "playlist-modify-public playlist-modify-private playlist-read-private user-library-read user-modify-playback-state user-read-playback-state"

def get_spotify():
    cache_path = os.path.join(os.path.dirname(__file__), ".cache")
    auth_manager = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=scope,
        open_browser=False,
        cache_path=cache_path
    )
    return spotipy.Spotify(auth_manager=auth_manager)

def get_target_playlist_id(sp):
    # Dynamic target from .env
    target_name = os.environ.get("TARGET_PLAYLIST_NAME", "Hans mix")
    playlists = sp.current_user_playlists()["items"]
    for p in playlists:
        if p['name'].lower() == target_name.lower():
            return p['id']
    # Create if missing
    user_id = sp.me()['id']
    new_p = sp.user_playlist_create(user_id, target_name, public=True, description=f"The official {target_name} DJ core.")
    return new_p['id']

def main():
    if not client_secret:
        print("Error: SPOTIPY_CLIENT_SECRET not set in environment or .env")
        return
        
    sp = get_spotify()
    
    if len(sys.argv) == 1:
        user = sp.current_user()
        print(f"Logged in as: {user['display_name']}")
        return

    cmd = sys.argv[1]

    if cmd == "list":
        playlists = sp.current_user_playlists()
        print(f"\n--- {sp.current_user()['display_name']}'s Playlists ---")
        for i, playlist in enumerate(playlists['items']):
            print(f"[{i}] {playlist['name'] : <30} | ID: {playlist['id']}")
            
    elif cmd == "tracks" and len(sys.argv) > 2:
        playlist_idx_or_id = sys.argv[2]
        if playlist_idx_or_id.isdigit():
            playlists = sp.current_user_playlists()
            idx = int(playlist_idx_or_id)
            playlist_id = playlists['items'][idx]['id'] if idx < len(playlists['items']) else None
        else:
            playlist_id = playlist_idx_or_id

        if not playlist_id:
            print("Playlist not found.")
            return

        results = sp.playlist_items(playlist_id)
        print(f"\n--- Tracks in {playlist_id} ---")
        for item in results['items']:
            if item and item.get('track'):
                track = item['track']
                print(f"- {track['name']} by {track['artists'][0]['name']} (ID: {track['id']})")

    elif cmd == "search" and len(sys.argv) > 2:
        query = " ".join(sys.argv[2:])
        results = sp.search(q=query, limit=5, type='track')
        print(f"\n--- Search Results for: {query} ---")
        for track in results['tracks']['items']:
            artists = ", ".join([a['name'] for a in track['artists']])
            print(f"- {track['name']} by {artists} (ID: {track['id']})")

    elif cmd == "dj" and len(sys.argv) > 2:
        query = " ".join(sys.argv[2:])
        results = sp.search(q=query, limit=1, type='track')
        if results['tracks']['items']:
            track = results['tracks']['items'][0]
            # Resolve target dynamically from .env
            playlist_id = get_target_playlist_id(sp)
            sp.playlist_add_items(playlist_id, [track['id']])
            print(f"✅ Added '{track['name']}' to targeting playlist!")
        else:
            print("❌ No match found.")

    elif cmd == "remove" and len(sys.argv) > 3:
        playlist_id = sys.argv[2]
        if playlist_id.isdigit():
            playlists = sp.current_user_playlists()
            playlist_id = playlists['items'][int(playlist_id)]['id']
        track_id = sys.argv[3]
        sp.playlist_remove_all_occurrences_of_items(playlist_id, [track_id])
        print(f"✅ Executed: Removed {track_id} from {playlist_id}")

    elif cmd == "play" and len(sys.argv) > 2:
        sp.start_playback(context_uri=f"spotify:playlist:{sys.argv[2]}")
        print(f"Playing {sys.argv[2]}...")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
