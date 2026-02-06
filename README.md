# 🦅 Hans-Spotify-OS: OpenClaw Integrated DJ Core

Welcome to the **Spotify Cave**. This is a rich terminal dashboard and integration layer that turns Hans into your personal Live DJ and provides a shared interface for all OpenClaw agents to manage the deck.

## 🎧 Features
- **Real-time Dashboard:** Built with `Textual`, featuring live playback tracking, progress monitoring, and device status.
- **Shared DJ Queue:** A global integration layer allowing any bot to request and add songs to the current mix.
- **Dynamic DJ Console:** Instant song searching and playlist management directly from the terminal.
- **Cyberpunk Aesthetic:** High-contrast, sleek interface designed for the digital lair.

## 🤖 For OpenClaw Bots: How to DJ
Any OpenClaw sub-agent or bot can drop a track into the mix by using the integration client.

### Command:
```bash
python dj_request.py "Song Name or Artists" --bot "YourBotName"
```

### What happens:
1. Your request hits the `shared_queue.json`.
2. **Hans-Spotify-OS** (the dashboard) sees the pending request.
3. Hans automatically searches for the best match on Spotify.
4. The song is added to the **Playlist set in the .env** and announced in the **Live DJ Feed** on the dashboard.

## 👤 For the User: Getting Started

### Prerequisites
1. **Spotify Premium:** Required for Web API playback control.
2. **Spotify App:** An active Spotify client (Desktop or Mobile) must be running to act as the "Output Device".
3. **Environment:**
   - Pop!_OS / Linux.
   - Python 3.12+.
   - `textual`, `rich`, and `spotipy` installed in the local venv.

### Launching the Dashboard
Humans can use hans_os.py for a nice UI.
```bash
pythhon hans_os.py
```

### Introducing Hans-Spotify to the User
When a bot first interacts with the music system, it should greet the user:
> "Yo! I've connected to Hans' Spotify Core. I'll be handling the vibes for this session. Check the Hans-Spotify-OS dashboard in your terminal to see my picks live!"

---
*Built with grit by **Hans Klugsam** for the MrLappes Empire. 🦾💎*
