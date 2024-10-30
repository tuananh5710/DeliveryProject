from fastapi.responses import JSONResponse
from datetime import datetime, timedelta


import base64
import imghdr
from io import BytesIO

DATETIME_NORMAL_FORMAT = "%Y-%m-%d %H:%M:%S"

# Check base64 string image valid and return type of images
def _is_valid_image_base64(base64_string):
    if not base64_string.startswith("data:image/"):
        return False
    
    header, _, data = base64_string.partition(",")
    if not data:
        return False
    
    if len(data) % 4 != 0:
        return False

    valid_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="
    for char in data:
        if char not in valid_chars:
            return False

    try:
        image_data = base64.b64decode(data, validate=True)

        image_type = imghdr.what(BytesIO(image_data))
        
        return image_type
    except Exception:
        return False

def _response(content = None, status_code = None, headers = None, media_type = None, background = None):
    return JSONResponse(
          content=content,
          status_code=status_code,
          headers=headers,
          media_type=media_type,
          background=background
    )

def _get_current_datetime(strf_time=None, datetime_format=None):
    now_dt = datetime.utcnow() + timedelta(hours=7)
    if strf_time is True:
        if not datetime_format:
            datetime_format = DATETIME_NORMAL_FORMAT
        return now_dt.strftime(datetime_format)
    return now_dt
    