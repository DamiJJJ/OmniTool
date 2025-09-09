import os
from flask import Blueprint, render_template, request, flash, jsonify
import requests

youtube_bp = Blueprint("youtube", __name__, url_prefix="/youtube")

YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")


@youtube_bp.route("/", methods=["GET"])
def latest_videos():
    video_id = request.args.get("video_id")
    channel_id = "UC1uYJszfaKTzbbz7jMiXBFg"

    if not YOUTUBE_API_KEY:
        error = "ERROR: YOUTUBE_API_KEY is not set in your .env file."
        print(error)
        flash(error, "danger")
        return render_template("youtube.html", videos=[], error=error)

    if video_id:
        video_stats = {}
        try:
            stats_url = f"https://www.googleapis.com/youtube/v3/videos?key={YOUTUBE_API_KEY}&id={video_id}&part=snippet,statistics"
            stats_response = requests.get(stats_url)
            stats_response.raise_for_status()
            stats_data = stats_response.json()

            if stats_data.get("items"):
                item = stats_data["items"][0]
                video_stats = {
                    "title": item["snippet"]["title"],
                    "published_at": item["snippet"]["publishedAt"],
                    "view_count": int(item["statistics"].get("viewCount", 0)),
                    "like_count": int(item["statistics"].get("likeCount", 0)),
                    "comment_count": int(item["statistics"].get("commentCount", 0)),
                }
        except requests.exceptions.RequestException as e:
            error = f"YouTube API connection error for video stats: {e}"
            print(error)
            flash(error, "danger")
        except Exception as e:
            error = f"An unexpected error occurred while fetching video stats: {e}"
            print(error)
            flash(error, "danger")

        return render_template(
            "youtube.html", video_id=video_id, video_stats=video_stats
        )

    videos = []
    error = None
    next_page_token = None

    try:
        url = f"https://www.googleapis.com/youtube/v3/search?key={YOUTUBE_API_KEY}&channelId={channel_id}&part=snippet,id&order=date&maxResults=10"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        next_page_token = data.get("nextPageToken")

        for item in data.get("items", []):
            if item["id"]["kind"] == "youtube#video":
                video_info = {
                    "title": item["snippet"]["title"],
                    "thumbnail_url": item["snippet"]["thumbnails"]["high"]["url"],
                    "video_id": item["id"]["videoId"],
                }
                videos.append(video_info)

    except requests.exceptions.RequestException as e:
        error = f"YouTube API connection error: {e}. Check your API key or internet connection."
        print(error)
        flash(error, "danger")
    except Exception as e:
        error = f"An unexpected error occurred: {e}"
        print(error)
        flash(error, "danger")

    return render_template(
        "youtube.html", videos=videos, error=error, next_page_token=next_page_token
    )


@youtube_bp.route("/load_more", methods=["GET"])
def load_more_videos():
    channel_id = "UC1uYJszfaKTzbbz7jMiXBFg"
    page_token = request.args.get("page_token")

    if not YOUTUBE_API_KEY or not page_token:
        return (
            jsonify(
                {
                    "videos": [],
                    "next_page_token": None,
                    "error": "Missing API key or page token.",
                }
            ),
            400,
        )

    try:
        url = f"https://www.googleapis.com/youtube/v3/search?key={YOUTUBE_API_KEY}&channelId={channel_id}&part=snippet,id&order=date&maxResults=10&pageToken={page_token}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        videos = []
        for item in data.get("items", []):
            if item["id"]["kind"] == "youtube#video":
                video_info = {
                    "title": item["snippet"]["title"],
                    "thumbnail_url": item["snippet"]["thumbnails"]["high"]["url"],
                    "video_id": item["id"]["videoId"],
                }
                videos.append(video_info)

        next_page_token = data.get("nextPageToken")
        return jsonify({"videos": videos, "next_page_token": next_page_token})

    except requests.exceptions.RequestException as e:
        error = f"YouTube API connection error: {e}"
        print(error)
        return jsonify({"videos": [], "next_page_token": None, "error": error}), 500
    except Exception as e:
        error = f"An unexpected error occurred: {e}"
        print(error)
        return jsonify({"videos": [], "next_page_token": None, "error": error}), 500
