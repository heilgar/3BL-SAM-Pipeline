import hmac
from hashlib import sha256

import requests

from secrets_manager import get_urlbox_credentials

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

def get_screenshot(url):
    api_key, api_secret = get_urlbox_credentials()

    args = {
        'url': url,
        'full_page': 'true',
        'width': 1280,
        'height': 800,
        'format': 'png',
        'timestamp': 'true',
        'response_type': 'binary'
    }

    query_string = urlencode(args, True)
    hmac_token = hmac.new(str.encode(api_secret), str.encode(query_string), sha256)
    token = hmac_token.hexdigest().rstrip('\n')

    screenshot_url = f"https://api.urlbox.io/v1/{api_key}/{token}/png?{query_string}"
    print(f"Generated Urlbox URL: {screenshot_url}")

    # Use requests to get the screenshot data
    response = requests.get(screenshot_url)

    if response.status_code == 200:
        return response.content  # Return the binary content of the image
    else:
        raise Exception(f"Failed to retrieve screenshot: {response.status_code} - {response.text}")
