#!/usr/bin/env python
import os
import sys
import getpass

# Ensure Django settings are discoverable
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms_backend.settings')

import django
django.setup()

from django.contrib.auth import get_user_model


def set_password_for_user(username: str):
    User = get_user_model()
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        print(f"User '{username}' does not exist.")
        return 2

    pwd = getpass.getpass(prompt=f"Enter new password for '{username}': ")
    pwd2 = getpass.getpass(prompt="Confirm password: ")
    if pwd != pwd2:
        print("Passwords do not match. Aborting.")
        return 3

    user.set_password(pwd)
    user.save()
    print(f"Password updated for user '{username}'.")
    return 0


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: set_password.py <username>")
        sys.exit(1)
    username = sys.argv[1]
    sys.exit(set_password_for_user(username))
