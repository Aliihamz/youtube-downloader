from flask import Flask, render_template, request
import yt_dlp
import os

app = Flask(__name__)

DOWNLOAD_FOLDER = "downloads"

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)


# ===============================
# YouTube Cookies Support (Render)
# ===============================

COOKIE_FILE = "cookies.txt"


def setup_cookies():

    cookies = os.getenv("COOKIES")

    if cookies:
        with open(COOKIE_FILE, "w", encoding="utf-8") as f:
            f.write(cookies)


setup_cookies()



def ydl_common_options():

    options = {
        "quiet": True,
        "noplaylist": True,
    }


    # Use cookies
    if os.path.exists(COOKIE_FILE):
        options["cookiefile"] = COOKIE_FILE


    return options



# ===============================
# Home
# ===============================

@app.route("/")
def home():
    return render_template("index.html")



# ===============================
# Get Video Info
# ===============================

@app.route("/download", methods=["POST"])
def download():

    url = request.form["url"]

    try:

        ydl_opts = ydl_common_options()


        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(
                url,
                download=False
            )


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





# ===============================
# Start Download
# ===============================

@app.route("/start-download", methods=["POST"])
def start_download():

    url = request.form["url"]
    quality = request.form["quality"]
    format_type = request.form["format"]


    try:


        ydl_opts = ydl_common_options()



        if format_type == "mp3":


            ydl_opts.update({

                "format": "bestaudio/best",

                "outtmpl":
                f"{DOWNLOAD_FOLDER}/%(title)s.%(ext)s",


                "postprocessors": [

                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192"
                    }

                ]

            })



        else:


            ydl_opts.update({

                "format":
                f"bestvideo[height<={quality}]+bestaudio/best",


                "outtmpl":
                f"{DOWNLOAD_FOLDER}/%(title)s.%(ext)s"

            })




        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            ydl.extract_info(
                url,
                download=True
            )



        return "Download Complete ✅"



    except Exception as e:

        return f"Error: {str(e)}"





if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000
    )