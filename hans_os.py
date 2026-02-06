from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, ListItem, ListView, Label, Button, Input
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import sys
import threading
import time

class SpotifyClient:
    def __init__(self):
        # Load from .env
        env_path = os.path.join(os.path.dirname(__file__), ".env")
        if os.path.exists(env_path):
            with open(env_path, "r") as f:
                for line in f:
                    if "SPOTIPY_CLIENT_SECRET" in line:
                        val = line.split("=")[1].strip().strip("'").strip('"')
                        os.environ["SPOTIPY_CLIENT_SECRET"] = val
                        break
        
        self.client_id = "969e1e690f344ecfa5cd51b453d2592c"
        self.redirect_uri = "http://localhost:8080/callback"
        self.scope = "playlist-modify-public playlist-modify-private playlist-read-private user-library-read user-modify-playback-state user-read-playback-state"
        
        cache_path = os.path.join(os.path.dirname(__file__), ".cache")
        self.auth_manager = SpotifyOAuth(
            client_id=self.client_id,
            redirect_uri=self.redirect_uri,
            scope=self.scope,
            open_browser=False,
            cache_path=cache_path
        )
        self.sp = spotipy.Spotify(auth_manager=self.auth_manager)

    def get_current_track(self):
        try:
            return self.sp.current_playback()
        except:
            return None

    def get_playlists(self):
        return self.sp.current_user_playlists()["items"]

class TrackInfo(Static):
    track_name = reactive("Unknown Track")
    artist_name = reactive("Unknown Artist")
    progress = reactive(0)
    is_playing = reactive(False)

    def render(self) -> str:
        play_icon = "▶" if self.is_playing else "⏸"
        return f"[bold cyan]{play_icon} {self.track_name}[/]\nby {self.artist_name}"

class DJLog(Static):
    logs = reactive([])

    def render(self) -> str:
        if not self.logs:
            return "[dim]No active DJ activity...[/]"
        return "\n".join(self.logs[-10:])

class HansSpotifyOS(App):
    CSS = """
    Container {
        layout: grid;
        grid-size: 2;
        grid-columns: 1fr 2fr;
    }
    #sidebar {
        background: $boost;
        border-right: solid white;
    }
    #main-content {
        padding: 1;
    }
    #dj-feed {
        height: 10;
        background: $surface;
        border: heavy magenta;
        padding: 0 1;
        margin-top: 1;
    }
    .playlist-item {
        padding: 0 1;
    }
    """

    def __init__(self):
        super().__init__()
        self.spotify = SpotifyClient()
        self.queue_file = os.path.join(os.path.dirname(__file__), "shared_queue.json")

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container():
            with Vertical(id="sidebar"):
                yield Label("[bold]Playlists[/]")
                playlists = self.spotify.get_playlists()
                yield ListView(*[ListItem(Static(p['name']), id=f"p_{p['id']}") for p in playlists])
            with Vertical(id="main-content"):
                yield TrackInfo(id="track-display")
                yield Horizontal(
                    Button("PREV", id="prev"),
                    Button("PLAY/PAUSE", id="toggle"),
                    Button("NEXT", id="skip"),
                )
                yield Label("\n[bold]Live DJ Feed (OpenClaw)[/]")
                yield DJLog(id="dj-log", classes="dj-feed-box")
                yield Input(placeholder="Search song to add to Hans Mix...", id="dj-search")
        yield Footer()

    def on_mount(self) -> None:
        self.update_timer = self.set_interval(5, self.update_playback)
        self.queue_timer = self.set_interval(3, self.check_shared_queue)

    def update_playback(self) -> None:
        track = self.spotify.get_current_track()
        if track and track.get('item'):
            display = self.query_one("#track-display")
            display.track_name = track['item']['name']
            display.artist_name = track['item']['artists'][0]['name']
            display.is_playing = track['is_playing']

    def check_shared_queue(self) -> None:
        if os.path.exists(self.queue_file):
            try:
                with open(self.queue_file, "r") as f:
                    data = json.load(f)
                
                pending = [r for r in data if r['status'] == 'pending']
                if pending:
                    log_widget = self.query_one("#dj-log")
                    new_logs = list(log_widget.logs)
                    
                    for req in pending:
                        # Process first one
                        query = req['song']
                        bot = req['bot']
                        
                        results = self.spotify.sp.search(q=query, limit=1, type='track')
                        if results['tracks']['items']:
                            track = results['tracks']['items'][0]
                            playlists = self.spotify.get_playlists()
                            self.spotify.sp.playlist_add_items(playlists[0]['id'], [track['id']])
                            new_logs.append(f"[bold magenta]{bot}:[/] 🎧 Added '{track['name']}'")
                        
                        req['status'] = 'processed'
                    
                    log_widget.logs = new_logs
                    with open(self.queue_file, "w") as f:
                        json.dump(data, f, indent=4)
            except Exception as e:
                pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "skip":
            self.spotify.sp.next_track()
        elif event.button.id == "prev":
            self.spotify.sp.previous_track()
        elif event.button.id == "toggle":
            playback = self.spotify.get_current_track()
            if playback and playback['is_playing']:
                self.spotify.sp.pause_playback()
            else:
                self.spotify.sp.start_playback()
        self.update_playback()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "dj-search":
            query = event.value
            results = self.spotify.sp.search(q=query, limit=1, type='track')
            if results['tracks']['items']:
                track = results['tracks']['items'][0]
                playlists = self.spotify.sp.current_user_playlists()
                # Index 0 is Hans Mix
                self.spotify.sp.playlist_add_items(playlists['items'][0]['id'], [track['id']])
                self.notify(f"Added {track['name']} to Hans Mix!")
                event.input.value = ""

if __name__ == "__main__":
    app = HansSpotifyOS()
    app.run()
