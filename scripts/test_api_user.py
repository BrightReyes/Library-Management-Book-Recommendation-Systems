import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'LMSFINAL'))

import api_client


def run_test():
    username = 'uitest1'
    email = 'uitest1@example.com'
    password = 'Secret123'
    try:
        res = api_client.create_user({'username': username, 'email': email, 'password': password})
        print('create_user response:', res)
    except Exception as e:
        print('create_user error:', e)

    try:
        res = api_client.login(username, password)
        print('login response:', res)
    except Exception as e:
        print('login error:', e)


if __name__ == '__main__':
    run_test()
