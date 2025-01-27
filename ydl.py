import yt_dlp
import shlex
import json
import sqlite3
from tempfile import NamedTemporaryFile

# just experimenting, let's see where this goes
# what im doing here:
# - extracting info from url and caching it
#   - this can be used to show video format, size etc before download
#   - NOTE: think about how long to cache it
# - downloading the video using that info json

OPTIONS = "--extract-audio --audio-format mp3 --audio-quality 2 --embed-metadata --embed-thumbnail"
URL = "http://localhost:3000/youtube_IoL8zsaoLTg_1080x1920_h264.mp4"

con = sqlite3.connect("ydlweb.db")
cur = con.cursor()

argv = ["--windows-filenames"]
argv.extend(shlex.split(OPTIONS))
argv.append(URL)

parsed_options = yt_dlp.parse_options(argv)

with yt_dlp.YoutubeDL(parsed_options.ydl_opts) as ydl:
    url = parsed_options.urls[0]
    # try to hit the cache first
    # cache invalid when? idk bruh
    cur.execute("select json from info where url=?", [url])
    res = cur.fetchone()
    if res is not None:
        info_json = res[0]
    else:
        # cache miss, fetch from network
        info = ydl.extract_info(url, download=False)
        # add to cache
        info_json = json.dumps(ydl.sanitize_info(info))
        cur.execute("insert into info values(?, ?)", [url, info_json])
        con.commit()

    # create a file to dump json temporarily
    # download_with_info_file needs it
    with NamedTemporaryFile(delete_on_close=False) as f:
        f.write(info_json.encode())
        f.close()
        ydl.download_with_info_file(f.name)

con.close()
