import io
import os

from flask import (
    Blueprint,
    render_template,
    request,
    flash,
    redirect,
    url_for,
    send_file,
    current_app,
)
from flask_wtf import FlaskForm
from wtforms import FileField, SelectField, SubmitField
from wtforms.validators import DataRequired
from PIL import Image

Image.MAX_IMAGE_PIXELS = 50_000_000

_MAGIC_CHECKS = [
    (lambda h: h[:3] == b'\xff\xd8\xff'),
    (lambda h: h[:8] == b'\x89PNG\r\n\x1a\n'),
    (lambda h: h[:6] in (b'GIF87a', b'GIF89a')),
    (lambda h: h[:2] == b'BM'),
    (lambda h: h[:4] in (b'II*\x00', b'MM\x00*')),
    (lambda h: h[:4] == b'RIFF' and h[8:12] == b'WEBP'),
]


def _is_valid_image(stream: io.BytesIO) -> bool:
    header = stream.read(12)
    stream.seek(0)
    return any(check(header) for check in _MAGIC_CHECKS)

conversion_bp = Blueprint("conversion", __name__, template_folder="../templates")

# Supported formats for the dropdowns (Pillow compatibility)
# Note: "JPG" is mapped to "JPEG" for PIL compatibility
IMAGE_FORMATS = [
    ("AUTO", "Auto Detect"),
    ("JPEG", "JPEG/JPG"),
    ("PNG", "PNG"),
    ("WEBP", "WebP"),
    ("GIF", "GIF"),
    ("BMP", "BMP"),
    ("TIFF", "TIFF/TIF"),
]

# Max file size in bytes (10 MB)
MAX_FILE_SIZE = 10 * 1024 * 1024


# Form for image conversion
class ConversionForm(FlaskForm):
    source_format = SelectField(
        "Convert From", choices=IMAGE_FORMATS, validators=[DataRequired()]
    )
    target_format = SelectField(
        "Convert To",
        choices=IMAGE_FORMATS[1:],
        validators=[DataRequired()],
    )
    file = FileField("Image File", validators=[DataRequired()])
    submit = SubmitField("Convert Image")


# --- Conversion Center Index ---
@conversion_bp.route("/convert", methods=["GET"])
def conversion_index():
    """Renders the main conversion hub with module selection."""
    return render_template("conversion_index.html")


# --- Image Conversion ---
@conversion_bp.route("/convert/image", methods=["GET", "POST"])
def image_conversion():
    """Renders the image conversion form (GET) and handles conversion logic (POST)."""
    form = ConversionForm()

    if request.method == "POST":
        if form.validate_on_submit():
            file = request.files.get("file")
            target_format = form.target_format.data

            if not file:
                flash("No file part or file not selected.", "danger")
                return redirect(url_for("conversion.image_conversion"))

            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)

            if file_size > MAX_FILE_SIZE:
                flash(
                    f"File size exceeds the limit of {MAX_FILE_SIZE / (1024 * 1024):.0f}MB.",
                    "danger",
                )
                return redirect(url_for("conversion.image_conversion"))

            try:
                image_stream = io.BytesIO(file.read())
                if not _is_valid_image(image_stream):
                    flash("Uploaded file is not a recognised image format.", "danger")
                    return redirect(url_for("conversion.image_conversion"))
                img = Image.open(image_stream)
                img.verify()
                image_stream.seek(0)
                img = Image.open(image_stream)

                pil_format = target_format

                if target_format in ["JPEG", "JPG"]:
                    pil_format = "JPEG"
                    if img.mode == "RGBA":
                        img.load()
                        background = Image.new("RGB", img.size, (255, 255, 255))
                        background.paste(img, mask=img.split()[3])
                        img = background

                elif target_format == "GIF":
                    img = img.convert("P") if img.mode != "P" else img

                output_stream = io.BytesIO()

                img.save(output_stream, format=pil_format)
                output_stream.seek(0)

                filename = (
                    f"converted_image.{target_format.lower().replace('jpeg', 'jpg')}"
                )

                mime_type = f"image/{target_format.lower()}"
                if pil_format == "JPEG":
                    mime_type = "image/jpeg"
                elif pil_format == "TIFF":
                    mime_type = "image/tiff"
                elif pil_format == "BMP":
                    mime_type = "image/bmp"

                return send_file(
                    output_stream,
                    mimetype=mime_type,
                    as_attachment=True,
                    download_name=filename,
                )

            except Exception as e:
                flash(f"An error occurred during conversion: {e}", "danger")
                return redirect(url_for("conversion.image_conversion"))

        flash(
            "Form validation failed. Please check your selection and try again.",
            "danger",
        )
        return redirect(url_for("conversion.image_conversion"))

    return render_template("image_conversion.html", form=form)


# --- Document/Text/PDF Conversion (Placeholder) ---
@conversion_bp.route("/convert/documents", methods=["GET"])
def document_conversion():
    """Displays the document/text/PDF tools page (Placeholder)."""
    return render_template("document_conversion.html")


# --- Archive Conversion (Placeholder) ---
@conversion_bp.route("/convert/archive", methods=["GET"])
def archive_conversion():
    """Displays the archive tools page (Placeholder)."""
    return render_template("archive_conversion.html")
