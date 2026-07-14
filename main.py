import os
import sys
import hmac
import hashlib
import json

import requests
from dotenv import load_dotenv


load_dotenv()


SECRET = os.getenv('API_SECRET', '')
ENDPOINT = os.getenv('API_ENDPOINT', '')
REQUIRED_FIELDS = [ 'name', 'email', 'resume', 'location', 'linkedin', 'codeLink' ]

def build_payload() -> dict:
    payload = {
        'name': os.getenv('APPLICANT_NAME', '').strip(),
        'email': os.getenv('APPLICANT_EMAIL', '').strip(),
        'resume': os.getenv('APPLICANT_RESUME_URL', '').strip(),
        'location': os.getenv('APPLICANT_LOCATION', '').strip(),
        'linkedin': os.getenv('APPLICANT_LINKEDIN_URL', '').strip(),
        'codeLink': os.getenv('APPLICANT_CODE_LINK', '').strip(),
        'yearsPython': 7,
        'yearsDjango': 4,
        'repos': os.getenv('APPLICANT_REPOS_URL', ''),
        'notes': '',
    }

    missing = [field for field in REQUIRED_FIELDS if not payload[field]]
    if missing:
        # Payload is malformed
        sys.exit(f'Missing required field(s): {",".join(missing)}')
    
    return payload


def sign(body: str, secret: str) -> str:
    return hmac.new(
        secret.encode(),
        body.encode(),
        hashlib.sha256
    ).hexdigest()


def main():
    payload = build_payload()

    body = json.dumps(payload, separators=(',', ':'))
    signature = sign(body, SECRET)

    headers = {
        "Content-Type": "application/json",
        "X-HMAC-Signature": signature,
    }

    try:
        resp = requests.post(ENDPOINT, data=body, headers=headers)
    except requests.RequestException as e:
        sys.exit(f'Request failed: {e}')

    if resp.status_code != requests.codes.created:
        print(f'Application failed with status {resp.status_code}')
        try: 
            print(json.dumps(resp.json(), indent=2))
        except ValueError:
            print(resp.text)
        sys.exit(1)
    
    print(json.dumps(resp.json(), indent=2))


if __name__ == '__main__':
    main()