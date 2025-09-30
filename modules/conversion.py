import os
from flask import (
    Blueprint,
    render_template,
    request,
    flash,
    redirect,
    url_for,
    send_file,
)
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
from wtforms import FileField, SelectField, SubmitField
from wtforms.validators import DataRequired
from PIL import Image
import io

conversion_bp = Blueprint("conversion", __name__, template_folder="../templates")

# Supported formats for the dropdowns
IMAGE_FORMATS = [
    ("JPG", "JPEG/JPG"),
    ("PNG", "PNG"),
    ("WEBP", "WebP"),
    ("GIF", "GIF"),
    ("BMP", "BMP"),
    ("TIFF", "TIFF/TIF"),
]

# Max file size in bytes (e.g., 10 MB)
MAX_FILE_SIZE = 10 * 1024 * 1024


# Form for image conversion
class ConversionForm(FlaskForm):
    source_format = SelectField(
        "Convert From", choices=IMAGE_FORMATS, validators=[DataRequired()]
    )
    target_format = SelectField(
        "Convert To", choices=IMAGE_FORMATS, validators=[DataRequired()]
    )
    file = FileField("Image File", validators=[DataRequired()])
    submit = SubmitField("Convert Image")


@conversion_bp.route("/conversion", methods=["GET"])
def conversion_page():
    """Renders the main conversion page (GET request)."""
    form = ConversionForm()
    return render_template("conversion.html", form=form)


@conversion_bp.route("/convert_image", methods=["POST"])
def convert_image():
    """Handles the image conversion logic (POST request)."""
    form = ConversionForm()

    if form.validate_on_submit():
        file = request.files.get("file")
        target_format = form.target_format.data

        if not file:
            flash("No file part or file not selected.", "danger")
            return redirect(url_for("conversion.conversion_page"))

        # Check file size before processing
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)

        if file_size > MAX_FILE_SIZE:
            flash(
                f"File size exceeds the limit of {MAX_FILE_SIZE / (1024 * 1024):.0f}MB.",
                "danger",
            )
            return redirect(url_for("conversion.conversion_page"))

        try:
            # 1. Read the image data into a stream
            image_stream = io.BytesIO(file.read())
            img = Image.open(image_stream)

            # 2. Check and handle RGBA mode for unsupported target formats (like JPEG)
            if img.mode == "RGBA" and target_format in ["JPG", "JPEG"]:
                img.load()
                background = Image.new("RGB", img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])
                img = background

            # 3. Create an in-memory output stream
            output_stream = io.BytesIO()
            pil_format = target_format if target_format != "JPG" else "JPEG"

            # 4. Save the converted image to the output stream
            img.save(output_stream, format=pil_format)
            output_stream.seek(0)

            # 5. Determine filename and mime type for download
            filename = f"converted_image.{target_format.lower()}"
            mime_type = f"image/{target_format.lower()}"
            if pil_format == "JPEG":
                mime_type = "image/jpeg"

            # 6. Send the file to the user
            return send_file(
                output_stream,
                mimetype=mime_type,
                as_attachment=True,
                download_name=filename,
            )

        except Exception as e:
            # Catch any general errors during file processing or conversion
            flash(f"An error occurred during conversion: {e}", "danger")
            return redirect(url_for("conversion.conversion_page"))

    # If form validation fails
    flash(
        "Form validation failed. Please check your selection and try again.", "danger"
    )
    return redirect(url_for("conversion.conversion_page"))
