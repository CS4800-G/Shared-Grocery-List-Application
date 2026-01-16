from flask import (Flask, flash, redirect, render_template, request, session,
                   url_for)
from storage import (add_item, add_list, add_user, analytics_all_lists,
                     calculate_totals, create_household, delete_item,
                     load_household, save_household)

app = Flask(__name__)
app.secret_key = "dev-secret-change-me"


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        join_code = request.form.get("join_code", "").strip()
        household_name = request.form.get("household_name", "").strip()

        if not username:
            flash("Username is required.")
            return redirect(url_for("index"))

        if household_name:
            join_code = create_household(household_name)
            data = load_household(join_code)
            add_user(data, username)
            save_household(join_code, data)

        elif join_code:
            data = load_household(join_code)
            if not data:
                flash("Invalid join code.")
                return redirect(url_for("index"))
            add_user(data, username)
            save_household(join_code, data)

        else:
            flash("Provide a join code or create a household.")
            return redirect(url_for("index"))

        session["username"] = username
        session["join_code"] = join_code
        session["current_list"] = "default"

        return redirect(url_for("household"))

    return render_template("index.html")


@app.route("/household", methods=["GET", "POST"])
def household():
    join_code = session.get("join_code")
    username = session.get("username")
    current_list = session.get("current_list", "default")

    if not join_code or not username:
        return redirect(url_for("index"))

    data = load_household(join_code)
    if not data:
        return redirect(url_for("index"))

    if request.method == "POST":
        if "new_list" in request.form:
            list_name = request.form["new_list"].strip()
            add_list(data, list_name)
            session["current_list"] = list_name

        elif "switch_list" in request.form:
            session["current_list"] = request.form["switch_list"]

        else:
            add_item(
                data,
                current_list,
                request.form["name"],
                int(request.form["quantity"]),
                float(request.form["price"]),
                username,
            )

        save_household(join_code, data)
        return redirect(url_for("household"))

    items = data["lists"][current_list]["items"]
    totals = calculate_totals(items)

    return render_template(
        "household.html",
        household=data["household"],
        user=username,
        join_code=join_code,
        lists=data["lists"],
        current_list=current_list,
        items=items,
        totals=totals,
    )


@app.route("/delete_item", methods=["POST"])
def delete_item_route():
    join_code = session.get("join_code")
    list_name = session.get("current_list")
    item_index = int(request.form["item_index"])

    if join_code and list_name:
        delete_item(join_code, list_name, item_index)

    return redirect(url_for("household"))


@app.route("/analytics")
def analytics():
    join_code = session.get("join_code")
    username = session.get("username")

    if not join_code or not username:
        return redirect(url_for("index"))

    data = load_household(join_code)
    if not data:
        return redirect(url_for("index"))

    analytics = analytics_all_lists(data)

    return render_template(
        "analytics.html",
        household=data["household"],
        analytics=analytics,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
