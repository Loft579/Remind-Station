import os
import requests

def report(content: str):
    user = os.environ.get('AGUSAVIOR_USERNAME', None)
    passw = os.environ.get('AGUSAVIOR_PASSWORD', None)
    if user is not None and passw is not None:
        try:
            r = requests.post('https://agusavior.com/tengoque', auth=(user, passw), json={
                'content': content,
            }, timeout=5)
            assert r.status_code <= 399
        except Exception as e:
            pass