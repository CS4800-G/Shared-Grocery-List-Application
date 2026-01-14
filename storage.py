import json
import random
import string
from datetime import datetime
from pathlib import Path

INSTANCE_DIR = Path("instance")
INSTANCE_DIR.mkdir(exist_ok=True)


def generate_join_code():
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=6))


def household_path(join_code):
    return INSTANCE_DIR / f"{join_code}.json"


def load_household(join_code):
    path = household_path(join_code)
    if not path.exists():
        return None
    with open(path, "r") as f:
        return json.load(f)


def save_household(join_code, data):
    with open(household_path(join_code), "w") as f:
        json.dump(data, f, indent=2)


def create_household(household_name):
    join_code = generate_join_code()
    data = {
        "household": {
            "name": household_name,
            "join_code": join_code
        },
        "users": [],
        "lists": {
            "default": {
                "items": []
            }
        }
    }
    save_household(join_code, data)
    return join_code


def add_user(data, username):
    if username not in data["users"]:
        data["users"].append(username)


def add_list(data, list_name):
    if list_name not in data["lists"]:
        data["lists"][list_name] = {"items": []}


def add_item(data, list_name, name, quantity, price, user):
    data["lists"][list_name]["items"].append({
        "name": name,
        "quantity": quantity,
        "price": price,
        "added_by": user,
        "created_at": datetime.utcnow().isoformat()
    })


def calculate_totals(items):
    totals = {}
    for item in items:
        user = item["added_by"]
        totals.setdefault(user, 0)
        totals[user] += item["quantity"] * item["price"]
    return totals
