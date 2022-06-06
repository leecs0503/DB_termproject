import psycopg2
from flask import Flask, render_template, request, redirect, session
from flask_cors import CORS


############ flask setting ############

app = Flask(__name__)
app.secret_key = "COSECOSECOSE"
CORS(app)
connect = psycopg2.connect(dbname="termproject", user="postgres", password="1234")
cur = connect.cursor()  # create cursor


############ no cache setting ############


@app.after_request
def set_response_headers(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    return r


############ main (login) page ############


@app.route("/", methods=["GET", "POST"])
def main():
    print(request.form)
    return render_template("main.html")


def validation_id(id):
    if len(id) == 0:
        return "id can't be empty"
    if len(id) >= 20:
        return f"id({id}) is so long (id's length should be shorter than 20)"
    return ""


def validation_password(password):
    if len(password) == 0:
        return "password can't be empty"
    if len(password) > 20:
        return f"password({password}) is so long (password's length should be shorter than 20)"
    return ""


def login(id: str, password: str):
    try:
        cur.execute("SELECT count(*) from users where id = %s and password = %s;", (id, password))
        result = cur.fetchall()
        if result[0][0] == 1:
            session["id"] = id
            return redirect("/action", code=302)
        else:
            return redirect("/login_failed", code=302)
    except Exception as err:
        return f"{err}"


def sign_up(id, password):
    try:
        print(id, password)
        cur.execute("SELECT count(*) from users where id = %s;", (id,))
        print(id, password)
        result = cur.fetchall()
        print(id, password)
        if result[0][0] == 1:
            return f"id {id} already exists try again"

        cur.execute("INSERT INTO users VALUES(%s, %s);", (id, password))
        cur.execute("INSERT INTO account VALUES(%s, %s, %s);", (id, 10000, "beginner"))
        return f"completely sign up id = {id} and password = {password}"
    except Exception as err:
        print(err)
        return f"{err}"


@app.route("/register", methods=["GET", "POST"])
def register():
    id = request.form["id"]
    password = request.form["password"]
    send = request.form["send"]

    err_msg = validation_id(id)
    if err_msg != "":
        return err_msg
    err_msg = validation_password(password)
    if err_msg != "":
        return err_msg

    if send == "login":
        return login(id=id, password=password)
    if send == "sign up":
        return sign_up(id=id, password=password)
    return "invalid request try again please"


@app.route("/login_failed", methods=["GET", "POST"])
def login_failed():
    return render_template("login_failed.html")


@app.route("/return", methods=["GET", "POST"])
def re_turn():
    print(request.form)
    return redirect("/", code=302)


############ main page ############


def users_info():
    cur.execute("SELECT * FROM users;")
    result = cur.fetchall()
    return render_template("users_info.html", users=result)


def trades_info():
    cur.execute("SELECT * FROM trade;")
    result = cur.fetchall()
    return render_template("trades_info.html", trades=result)


@app.route("/admin_func", methods=["GET", "POST"])
def admin_func():
    print(request.form)
    send = request.form["send"]
    if send == "users_info":
        return users_info()
    if send == "trades_info":
        return trades_info()
    return "invalid request try again please"


@app.route("/logout", methods=["GET", "POST"])
def logout():
    session["id"] = ""
    print(request.form)
    return redirect("/", code=302)


def get_popular_category():
    sql = """
        select c.type
            from category as c, (
            	SELECT code, COUNT(code) as cnt
            	FROM trade
            	GROUP BY code) as G
            where c.code = G.code
            order by G.cnt DESC
            limit 1;
    """
    cur.execute(sql)
    result = cur.fetchall()
    if len(result) == 0:
        return "there is no item"
    return result[0][0]


def get_best_people(type):
    sql = f"""
        select {type}, sum(trade_price) as S
            from trade
            GROUP BY {type}
            ORDER BY S DESC
            limit 1;
    """
    cur.execute(sql)
    result = cur.fetchall()
    if len(result) == 0:
        return f"there is no {type}"
    return result[0][0]


def get_user_info(id):
    sql = """
        SELECT * FROM account where id = %s;
    """
    print(id)
    cur.execute(sql, (id,))
    result = cur.fetchall()
    return {
        "id": result[0][0],
        "balance": result[0][1],
        "rating": result[0][2],
    }


def get_all_items():
    sql = """
        SELECT * FROM items;
    """
    cur.execute(sql)
    result = cur.fetchall()
    return result


@app.route("/action")
def action():
    print(request.form)

    id = session["id"]
    popular_category = get_popular_category()
    best_buyer = get_best_people("buyer")
    best_seller = get_best_people("seller")
    items = get_all_items()
    user_info = get_user_info(id)

    return render_template(
        "action.html",
        admin_display="show" if id == "admin" else "none",
        id=id,
        balance=user_info["balance"],
        rating=user_info["rating"],
        popular_category=popular_category,
        best_buyer=best_buyer,
        best_seller=best_seller,
        items=items,
    )


############ item add page ############
@app.route("/item_add")
def item_add():
    return render_template("main.html")


############ item buy page ############
@app.route("/item_buy")
def item_buy():
    return render_template("main.html")


############ item buying page ############
@app.route("/item_buying")
def item_buying():
    return render_template("main.html")


############ etc ############
@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, "static"), "favicon.ico", mimetype="image/vnd.microsoft.icon"
    )


############ main ############
if __name__ == "__main__":
    app.run()
