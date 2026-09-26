from flask import Flask, render_template, request, send_file
import yt_dlp
import os

app = Flask(__name__)

DOWNLOAD_FOLDER = "downloads"

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/download", methods=["POST"])
def download():

    url = request.form["url"]

    try:
        ydl_opts = {
            "quiet": True,
            "noplaylist": True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        title = info.get("title")
        thumbnail = info.get("thumbnail")
        duration = info.get("duration")

        formats = info.get("formats", [])

        qualities = []

        for f in formats:
            height = f.get("height")

            if height and height not in qualities:
                qualities.append(height)

        qualities.sort(reverse=True)

        quality_names = []

        for q in qualities:
            if q >= 2160:
                quality_names.append("2160p 4K")
            elif q >= 1440:
                quality_names.append("1440p 2K")
            elif q >= 1080:
                quality_names.append("1080p Full HD")
            elif q >= 720:
                quality_names.append("720p HD")
            else:
                quality_names.append(f"{q}p")


        return render_template(
            "result.html",
            title=title,
            thumbnail=thumbnail,
            duration=duration,
            qualities=quality_names,
            url=url
        )


    except Exception as e:
        return f"Error: {str(e)}"



@app.route("/start-download", methods=["POST"])
def start_download():

    url = request.form["url"]
    quality = request.form["quality"]
    format_type = request.form["format"]


    try:

        if format_type == "mp3":

            ydl_opts = {
                "format": "bestaudio",
                "outtmpl": f"{DOWNLOAD_FOLDER}/%(title)s.%(ext)s",
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3"
                    }
                ]
            }

        else:

            ydl_opts = {
                "format": f"bestvideo[height<={quality}]+bestaudio/best",
                "outtmpl": f"{DOWNLOAD_FOLDER}/%(title)s.%(ext)s"
            }


        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

            filename = ydl.prepare_filename(info)


        return "Download Complete ✅"


    except Exception as e:
        return f"Error: {str(e)}"



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)