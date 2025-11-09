import os
from django.core.exceptions import ValidationError

# ✅ List of allowed file types
ALLOWED_EXTENSIONS = {'.pdf', '.jpg', '.jpeg', '.png'}

def validate_upload_file(file):
    """
    Simple validator to restrict uploads to safe file types.
    No dependency on python-magic, so it runs cleanly on Render.
    """
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError(
            f"Invalid file type: {ext}. Only PDF and image files are allowed."
        )
