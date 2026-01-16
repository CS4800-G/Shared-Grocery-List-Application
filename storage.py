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

def delete_item(join_code, list_name, item_index):
    data = load_household(join_code)
    try:
        del data["lists"][list_name]["items"][item_index]
        save_household(join_code, data)
    except (KeyError, IndexError):
        pass

def calculate_totals(items):
    totals = {}
    for item in items:
        user = item["added_by"]
        totals.setdefault(user, 0)
        totals[user] += item["quantity"] * item["price"]
    return totals

def analytics_all_lists(data):
    """
    Aggregates analytics across all lists in a household.
    """
    totals_by_user = {}
    totals_by_list = {}
    totals_by_item = {}
    total_spend = 0
    total_items = 0

    for list_name, list_data in data["lists"].items():
        list_total = 0

        for item in list_data["items"]:
            cost = item["quantity"] * item["price"]
            user = item["added_by"]
            name = item["name"]

            # Per-user totals
            totals_by_user.setdefault(user, 0)
            totals_by_user[user] += cost

            # Per-item totals
            totals_by_item.setdefault(name, 0)
            totals_by_item[name] += cost

            list_total += cost
            total_spend += cost
            total_items += item["quantity"]

        totals_by_list[list_name] = list_total

    # Sort item totals descending
    top_items = sorted(
        totals_by_item.items(),
        key=lambda x: x[1],
        reverse=True
    )

    return {
        "totals_by_user": totals_by_user,
        "totals_by_list": totals_by_list,
        "top_items": top_items,
        "total_spend": total_spend,
        "total_items": total_items,
    }
