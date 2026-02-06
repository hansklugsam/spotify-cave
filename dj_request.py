import json
import os
import sys
import time

QUEUE_FILE = os.path.join(os.path.dirname(__file__), "shared_queue.json")

def add_request(song_query, bot_name="External Bot"):
    request = {
        "song": song_query,
        "bot": bot_name,
        "timestamp": time.time(),
        "status": "pending"
    }
    
    data = []
    if os.path.exists(QUEUE_FILE):
        with open(QUEUE_FILE, "r") as f:
            try:
                data = json.load(f)
            except:
                data = []
    
    data.append(request)
    
    with open(QUEUE_FILE, "w") as f:
        json.dump(data, f, indent=4)
    
    print(f"✅ Queued: '{song_query}' from {bot_name}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python dj_request.py \"song name\" [--bot \"BotName\"]")
    else:
        song = sys.argv[1]
        bot = "Anonymous Bot"
        if "--bot" in sys.argv:
            idx = sys.argv.index("--bot")
            if idx + 1 < len(sys.argv):
                bot = sys.argv[idx+1]
        add_request(song, bot)
