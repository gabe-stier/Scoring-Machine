from hashlib import blake2b
import os
from datetime import datetime

def generate_token():
    if os.path.exists('/tmp/scoring_token'):
        with open('/tmp/scoring_token', 'r') as f:
            return f.read()
    else:
        with open('/tmp/scoring_token', 'w') as f:
            m = blake2b(salt=b'semo')
            m.update(str(datetime.now()).encode())
            token = m.hexdigest()
            f.write(token)
            return token
