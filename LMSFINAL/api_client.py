import requests
from typing import Optional, Dict, Any

API_BASE = "http://127.0.0.1:8000/api"

_token: Optional[str] = None


def set_token(token: Optional[str]):
    global _token
    _token = token


def _headers():
    headers = {"Content-Type": "application/json"}
    if _token:
        headers["Authorization"] = f"Bearer {_token}"
    return headers


def _request(method: str, url: str, **kwargs):
    """Helper to perform HTTP requests and raise informative errors."""
    try:
        r = requests.request(method, url, **kwargs)
    except requests.RequestException as e:
        raise Exception(f"Network error: {e}")

    if r.status_code >= 400:
        # try to extract JSON error message
        try:
            err = r.json()
        except Exception:
            err = r.text
        raise Exception(f"{r.status_code} {r.reason}: {err}")

    try:
        return r.json()
    except Exception:
        return r.text


def login(username: str, password: str) -> Dict[str, Any]:
    """Obtain JWT token pair."""
    url = f"{API_BASE}/auth/login/"
    data = _request('post', url, json={"username": username, "password": password})
    access = data.get("access") if isinstance(data, dict) else None
    if access:
        set_token(access)
    return data


def get_me() -> Dict[str, Any]:
    url = f"{API_BASE}/users/me/"
    r = requests.get(url, headers=_headers())
    r.raise_for_status()
    return r.json()


def get_books() -> list:
    url = f"{API_BASE}/books/"
    r = requests.get(url, headers=_headers())
    r.raise_for_status()
    return r.json()


def get_book(book_id: int) -> dict:
    url = f"{API_BASE}/books/{book_id}/"
    r = requests.get(url, headers=_headers())
    r.raise_for_status()
    return r.json()


def create_book(payload: dict) -> dict:
    url = f"{API_BASE}/books/"
    r = requests.post(url, json=payload, headers=_headers())
    r.raise_for_status()
    return r.json()


def update_book(book_id: int, payload: dict) -> dict:
    url = f"{API_BASE}/books/{book_id}/"
    r = requests.put(url, json=payload, headers=_headers())
    r.raise_for_status()
    return r.json()


def delete_book(book_id: int) -> None:
    url = f"{API_BASE}/books/{book_id}/"
    r = requests.delete(url, headers=_headers())
    r.raise_for_status()


def create_user(payload: dict) -> dict:
    url = f"{API_BASE}/users/"
    return _request('post', url, json=payload, headers=_headers())


def get_users() -> list:
    url = f"{API_BASE}/users/"
    r = requests.get(url, headers=_headers())
    r.raise_for_status()
    return r.json()


def update_user(user_id: int, payload: dict) -> dict:
    url = f"{API_BASE}/users/{user_id}/"
    r = requests.put(url, json=payload, headers=_headers())
    r.raise_for_status()
    return r.json()


def delete_user(user_id: int) -> None:
    url = f"{API_BASE}/users/{user_id}/"
    r = requests.delete(url, headers=_headers())
    r.raise_for_status()


def get_loans(user_id: Optional[int] = None, status: Optional[str] = None) -> list:
    url = f"{API_BASE}/loans/"
    params = {}
    if user_id is not None:
        params['user'] = user_id
    if status is not None:
        params['status'] = status
    r = requests.get(url, headers=_headers(), params=params)
    r.raise_for_status()
    return r.json()


def create_loan(payload: dict) -> dict:
    url = f"{API_BASE}/loans/"
    r = requests.post(url, json=payload, headers=_headers())
    r.raise_for_status()
    return r.json()


def return_loan(loan_id: int) -> dict:
    url = f"{API_BASE}/loans/{loan_id}/return/"
    r = requests.post(url, headers=_headers())
    r.raise_for_status()
    return r.json()
