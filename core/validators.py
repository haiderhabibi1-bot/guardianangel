import magic
from django.core.exceptions import ValidationError
from django.conf import settings

def validate_upload_file(file_obj):
    """
    Validates uploaded files to prevent unsafe or oversized uploads.
    - Max size: 2 MB
    - Allowed types: PDF, PNG, JPEG
    """

    # 1️⃣ Check size
    max_size = getattr(settings, 'MAX_UPLOAD_SIZE_BYTES', 2 * 1024 * 1024)  # default 2 MB
    if file_obj.size > max_size:
        raise ValidationError('File too large. Maximum allowed size is 2 MB.')

    # 2️⃣ Check MIME type
    try:
        file_obj.seek(0)
        mime = magic.from_buffer(file_obj.read(2048), mime=True)
        file_obj.seek(0)
    except Exception:
        raise ValidationError('Unable to validate file type.')

    allowed_mime = getattr(
        settings,
        'ALLOWED_UPLOAD_MIME',
        ['application/pdf', 'image/png', 'image/jpeg']
    )

    if mime not in allowed_mime:
        raise ValidationError('Unsupported file type. Only PDF, JPEG, or PNG are allowed.')
