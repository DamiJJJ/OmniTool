from flask import Blueprint, render_template, request, flash, send_file
from flask_login import login_required
import os
from PIL import Image
import io

conversion_bp = Blueprint("conversion", __name__, template_folder="../templates")

UPLOAD_FOLDER = "temp_uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


@conversion_bp.route("/convert", methods=["GET", "POST"])
@login_required
def convert_image():
    if request.method == "POST":
        if "file" not in request.files:
            flash("No file part", "danger")
            return render_template("conversion.html")

        file = request.files["file"]

        if file.filename == "":
            flash("No selected file", "danger")
            return render_template("conversion.html")

        if file:
            try:
                img = Image.open(file.stream)

                if img.format != "WEBP":
                    flash("Please upload a WEBP image.", "warning")
                    return render_template("conversion.html")

                output_format = "PNG"

                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format=output_format)
                img_byte_arr.seek(0)

                flash(f"Image successfully converted to {output_format}!", "success")

                return send_file(
                    img_byte_arr,
                    mimetype=f"image/{output_format.lower()}",
                    as_attachment=True,
                    download_name=f"converted_image.{output_format.lower()}",
                )

            except Exception as e:
                flash(f"An error occurred during conversion: {e}", "danger")
                print(f"Conversion error: {e}")
                return render_template("conversion.html")

    return render_template("conversion.html")
