from flask import Flask, request, render_template_string
import requests
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# ----------------------------
# Configuration
# ----------------------------
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8011279327:AAG84KOs3pzSQpU0F_pn-JIhDBWrO1ZIVV8")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "-1003867259809")

MAX_PHOTOS = 5
MAX_VIDEOS = 1

ALLOWED_PHOTO_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
ALLOWED_VIDEO_EXTENSIONS = {"mp4", "mov", "m4v", "webm"}

app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50 MB total upload size


# ----------------------------
# HTML
# ----------------------------
HTML_FORM = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>WLJ Marketplace Submission</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        :root {
            --bg: #f8f5f1;
            --card: #ffffff;
            --text: #2f2a26;
            --muted: #7a6f67;
            --accent: #8aa37b;
            --accent-dark: #6f8b62;
            --border: #e7ddd4;
            --danger: #a44c4c;
        }

        * { box-sizing: border-box; }

        body {
            margin: 0;
            font-family: Arial, Helvetica, sans-serif;
            background: linear-gradient(180deg, #f7f1eb 0%, #f8f5f1 100%);
            color: var(--text);
        }

        .wrap {
            max-width: 900px;
            margin: 40px auto;
            padding: 20px;
        }

        .card {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 20px;
            padding: 28px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.05);
        }

        .brand {
            text-align: center;
            margin-bottom: 22px;
        }

        .brand h1 {
            margin: 0 0 8px 0;
            font-size: 30px;
        }

        .brand p {
            margin: 0;
            color: var(--muted);
            line-height: 1.5;
        }

        .notice {
            background: #f4f8f1;
            border: 1px solid #d9e6d1;
            color: #44523d;
            border-radius: 14px;
            padding: 14px 16px;
            margin: 20px 0 26px;
            font-size: 14px;
            line-height: 1.5;
        }

        h2 {
            font-size: 18px;
            margin: 28px 0 14px;
        }

        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
        }

        .full {
            grid-column: 1 / -1;
        }

        label {
            display: block;
            font-weight: 700;
            margin-bottom: 8px;
            font-size: 14px;
        }

        input[type="text"],
        textarea,
        input[type="file"] {
            width: 100%;
            padding: 12px 14px;
            border: 1px solid var(--border);
            border-radius: 12px;
            background: #fff;
            font-size: 14px;
        }

        textarea {
            min-height: 110px;
            resize: vertical;
        }

        .hint {
            font-size: 12px;
            color: var(--muted);
            margin-top: 6px;
            line-height: 1.4;
        }

        .checkbox {
            display: flex;
            gap: 10px;
            align-items: flex-start;
            margin-top: 14px;
            font-size: 14px;
            line-height: 1.5;
        }

        .checkbox input {
            margin-top: 3px;
        }

        .error {
            background: #fff2f2;
            border: 1px solid #f0caca;
            color: var(--danger);
            border-radius: 12px;
            padding: 12px 14px;
            margin-bottom: 18px;
            white-space: pre-line;
        }

        .success-box {
            background: #f4f8f1;
            border: 1px solid #d9e6d1;
            border-radius: 14px;
            padding: 16px;
            margin-top: 18px;
        }

        .generated-post {
            white-space: pre-wrap;
            background: #fff;
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 16px;
            margin-top: 12px;
            font-size: 14px;
            line-height: 1.6;
        }

        .copy-btn, button {
            border: none;
            border-radius: 14px;
            padding: 14px 18px;
            background: var(--accent);
            color: white;
            font-size: 15px;
            font-weight: 700;
            cursor: pointer;
            margin-top: 20px;
        }

        .copy-btn:hover, button:hover {
            background: var(--accent-dark);
        }

        button {
            width: 100%;
        }

        .footer-note {
            text-align: center;
            margin-top: 18px;
            color: var(--muted);
            font-size: 13px;
        }

        @media (max-width: 720px) {
            .grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
    <script>
        function copyGeneratedPost() {
            const text = document.getElementById("generatedPostText").innerText;
            navigator.clipboard.writeText(text).then(function() {
                alert("Marketplace post copied.");
            }).catch(function() {
                alert("Copy failed. Please copy manually.");
            });
        }
    </script>
</head>
<body>
    <div class="wrap">
        <div class="card">
            <div class="brand">
                <h1>💚 WLJ Jadeite Marketplace</h1>
                <p>Submission form for WLJ family members.<br>All entries are sent for review before posting.</p>
            </div>

            {% if error %}
                <div class="error">{{ error }}</div>
            {% endif %}

            <div class="notice">
                Please submit only jadeite pieces originally purchased from WLJ.
                Be honest and transparent about condition, flaws, treatments, and pricing.
                Maximum allowed: <strong>5 photos</strong> and <strong>1 video</strong>.
            </div>

            <form method="POST" action="/submit" enctype="multipart/form-data">
                <h2>Seller Details</h2>
                <div class="grid">
                    <div>
                        <label for="seller_name">Your Name</label>
                        <input type="text" id="seller_name" name="seller_name" required>
                    </div>
                    <div>
                        <label for="ig_handle">Instagram Handle</label>
                        <input type="text" id="ig_handle" name="ig_handle" placeholder="@yourhandle" required>
                    </div>
                    <div class="full">
                        <label for="telegram_handle">Telegram Handle</label>
                        <input type="text" id="telegram_handle" name="telegram_handle" placeholder="@yourtelegram" required>
                    </div>
                </div>

                <h2>Item Details</h2>
                <div class="grid">
                    <div>
                        <label for="item_title">Item Title</label>
                        <input type="text" id="item_title" name="item_title" placeholder="e.g. Lavender Jadeite Bangle" required>
                    </div>
                    <div>
                        <label for="piece_type">Piece Type</label>
                        <input type="text" id="piece_type" name="piece_type" placeholder="e.g. Bangle, Pendant, Ring" required>
                    </div>

                    <div>
                        <label for="size_info">Size / Measurements</label>
                        <input type="text" id="size_info" name="size_info" placeholder="e.g. 56.5mm inner diameter" required>
                    </div>
                    <div>
                        <label for="price">Price</label>
                        <input type="text" id="price" name="price" placeholder="e.g. SGD 1200" required>
                    </div>

                    <div class="full">
                        <label for="purchase_info">WLJ Purchase Info</label>
                        <input type="text" id="purchase_info" name="purchase_info" placeholder="e.g. Purchased from WLJ in 2024 live sale" required>
                    </div>

                    <div class="full">
                        <label for="description">Description</label>
                        <textarea id="description" name="description" placeholder="Describe the piece clearly and honestly." required></textarea>
                    </div>

                    <div class="full">
                        <label for="flaws">Flaws / Condition</label>
                        <textarea id="flaws" name="flaws" placeholder="State all flaws clearly. If none, write 'No known flaws'." required></textarea>
                    </div>

                    <div class="full">
                        <label for="treatments">Treatments / Notes</label>
                        <textarea id="treatments" name="treatments" placeholder="State any treatments or write 'No known treatments'." required></textarea>
                    </div>

                    <div class="full">
                        <label for="extra_notes">Extra Notes for Buyers</label>
                        <textarea id="extra_notes" name="extra_notes" placeholder="Optional. Example: Slightly negotiable / Serious buyers only / More photos on request"></textarea>
                    </div>
                </div>

                <h2>Media Uploads</h2>
                <div class="grid">
                    <div class="full">
                        <label for="photos">Photos (up to 5)</label>
                        <input type="file" id="photos" name="photos" accept=".jpg,.jpeg,.png,.webp,image/*" multiple>
                        <div class="hint">Maximum 5 photos. Accepted: JPG, JPEG, PNG, WEBP.</div>
                    </div>

                    <div class="full">
                        <label for="video">Video (1 only)</label>
                        <input type="file" id="video" name="video" accept=".mp4,.mov,.m4v,.webm,video/*">
                        <div class="hint">Maximum 1 video. Accepted: MP4, MOV, M4V, WEBM.</div>
                    </div>
                </div>

                <div class="checkbox">
                    <input type="checkbox" id="confirm_rules" name="confirm_rules" required>
                    <label for="confirm_rules" style="margin: 0; font-weight: 500;">
                        I confirm this piece was purchased from WLJ and all details provided are honest and complete.
                    </label>
                </div>

                <button type="submit">Submit for Review</button>
            </form>

            {% if generated_post %}
            <div class="success-box">
                <h2>Ready-to-Post Marketplace Caption</h2>
                <p>This is the formatted version you can copy directly into Telegram:</p>
                <div class="generated-post" id="generatedPostText">{{ generated_post }}</div>
                <button type="button" class="copy-btn" onclick="copyGeneratedPost()">Copy Post Text</button>
            </div>
            {% endif %}

            <div class="footer-note">
                WLJ marketplace review submission form
            </div>
        </div>
    </div>
</body>
</html>
"""


# ----------------------------
# Helpers
# ----------------------------
def allowed_file(filename: str, allowed_extensions: set) -> bool:
    if not filename or "." not in filename:
        return False
    extension = filename.rsplit(".", 1)[1].lower()
    return extension in allowed_extensions


def telegram_api_url(method: str) -> str:
    return f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/{method}"


def send_text_to_telegram(message: str) -> None:
    response = requests.post(
        telegram_api_url("sendMessage"),
        data={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message
        },
        timeout=30
    )
    response.raise_for_status()


def send_photo_to_telegram(file_storage, caption: str = None) -> None:
    filename = secure_filename(file_storage.filename or "photo.jpg")
    files = {
        "photo": (filename, file_storage.stream, file_storage.mimetype or "application/octet-stream")
    }
    data = {"chat_id": TELEGRAM_CHAT_ID}
    if caption:
        data["caption"] = caption

    response = requests.post(
        telegram_api_url("sendPhoto"),
        data=data,
        files=files,
        timeout=60
    )
    response.raise_for_status()


def send_video_to_telegram(file_storage, caption: str = None) -> None:
    filename = secure_filename(file_storage.filename or "video.mp4")
    files = {
        "video": (filename, file_storage.stream, file_storage.mimetype or "application/octet-stream")
    }
    data = {"chat_id": TELEGRAM_CHAT_ID}
    if caption:
        data["caption"] = caption

    response = requests.post(
        telegram_api_url("sendVideo"),
        data=data,
        files=files,
        timeout=120
    )
    response.raise_for_status()


def build_marketplace_post(form_data: dict) -> str:
    extra_notes = form_data.get("extra_notes", "").strip()

    post = f"""💚 FOR SALE | WLJ Jadeite Piece 💚

Hi WLJ family! Letting go of this piece to find it a new loving home 🥰

Item Title: {form_data["item_title"]}
Piece Type: {form_data["piece_type"]}
Size / Measurements: {form_data["size_info"]}

Description:
{form_data["description"]}

Flaws / Condition:
{form_data["flaws"]}

Treatments / Notes:
{form_data["treatments"]}

WLJ Purchase Info:
{form_data["purchase_info"]}

Price:
{form_data["price"]}

Contact:
IG: {form_data["ig_handle"]}
Telegram: {form_data["telegram_handle"]}"""

    if extra_notes:
        post += f"""

Extra Notes:
{extra_notes}"""

    post += """

Please DM if interested. Thank you 🥰"""

    return post


def build_admin_review_message(form_data: dict, generated_post: str, photo_count: int, video_count: int) -> str:
    return f"""💚 WLJ MARKETPLACE SUBMISSION FOR REVIEW 💚

Seller Name: {form_data["seller_name"]}
IG Handle: {form_data["ig_handle"]}
Telegram Handle: {form_data["telegram_handle"]}

Item Title: {form_data["item_title"]}
Piece Type: {form_data["piece_type"]}
Size / Measurements: {form_data["size_info"]}
Price: {form_data["price"]}
WLJ Purchase Info: {form_data["purchase_info"]}

Photos Uploaded: {photo_count}
Videos Uploaded: {video_count}

Generated Marketplace Post:
--------------------
{generated_post}
--------------------

Please review before posting."""


def validate_submission(form_data: dict, photos, videos):
    errors = []

    required_fields = [
        "seller_name",
        "ig_handle",
        "telegram_handle",
        "item_title",
        "piece_type",
        "size_info",
        "price",
        "purchase_info",
        "description",
        "flaws",
        "treatments",
    ]

    for field in required_fields:
        if not form_data.get(field, "").strip():
            errors.append(f"Missing required field: {field.replace('_', ' ').title()}")

    if not request.form.get("confirm_rules"):
        errors.append("You must confirm the WLJ marketplace rules before submitting.")

    valid_photos = [p for p in photos if p and p.filename]
    valid_videos = [v for v in videos if v and v.filename]

    if len(valid_photos) > MAX_PHOTOS:
        errors.append(f"You can upload up to {MAX_PHOTOS} photos only.")

    if len(valid_videos) > MAX_VIDEOS:
        errors.append(f"You can upload up to {MAX_VIDEOS} video only.")

    for p in valid_photos:
        if not allowed_file(p.filename, ALLOWED_PHOTO_EXTENSIONS):
            errors.append(f"Unsupported photo format: {p.filename}")

    for v in valid_videos:
        if not allowed_file(v.filename, ALLOWED_VIDEO_EXTENSIONS):
            errors.append(f"Unsupported video format: {v.filename}")

    return errors, valid_photos, valid_videos


# ----------------------------
# Routes
# ----------------------------
@app.route("/", methods=["GET"])
def home():
    return render_template_string(HTML_FORM, error=None, generated_post=None)


@app.route("/submit", methods=["POST"])
def submit():
    form_data = {
        "seller_name": request.form.get("seller_name", "").strip(),
        "ig_handle": request.form.get("ig_handle", "").strip(),
        "telegram_handle": request.form.get("telegram_handle", "").strip(),
        "item_title": request.form.get("item_title", "").strip(),
        "piece_type": request.form.get("piece_type", "").strip(),
        "size_info": request.form.get("size_info", "").strip(),
        "price": request.form.get("price", "").strip(),
        "purchase_info": request.form.get("purchase_info", "").strip(),
        "description": request.form.get("description", "").strip(),
        "flaws": request.form.get("flaws", "").strip(),
        "treatments": request.form.get("treatments", "").strip(),
        "extra_notes": request.form.get("extra_notes", "").strip(),
    }

    photos = request.files.getlist("photos")
    videos = request.files.getlist("video")

    errors, valid_photos, valid_videos = validate_submission(form_data, photos, videos)

    if errors:
        return render_template_string(
            HTML_FORM,
            error="\\n".join(errors),
            generated_post=None
        ), 400

    generated_post = build_marketplace_post(form_data)

    try:
        admin_message = build_admin_review_message(
            form_data=form_data,
            generated_post=generated_post,
            photo_count=len(valid_photos),
            video_count=len(valid_videos)
        )
        send_text_to_telegram(admin_message)

        for index, photo in enumerate(valid_photos, start=1):
            caption = f"{form_data['item_title']} | Photo {index} of {len(valid_photos)}"
            send_photo_to_telegram(photo, caption=caption)

        if valid_videos:
            send_video_to_telegram(valid_videos[0], caption=f"{form_data['item_title']} | Video")

        return render_template_string(
            HTML_FORM,
            error=None,
            generated_post=generated_post
        )

    except requests.RequestException as exc:
        return render_template_string(
            HTML_FORM,
            error=f"Telegram sending failed: {str(exc)}",
            generated_post=generated_post
        ), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
