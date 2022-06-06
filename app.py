import psycopg2
from flask import Flask, render_template, request, redirect, session
from flask_cors import CORS


app = Flask(__name__)
app.secret_key = 'COSECOSECOSE'
CORS(app)
connect = psycopg2.connect(dbname="termproject", user="postgres", password="1234")
cur = connect.cursor()  # create cursor



############ no cache setting ############

@app.after_request
def set_response_headers(r):
    r.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    r.headers['Pragma'] = 'no-cache'
    r.headers['Expires'] = '0'
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
            session['id'] = id
            return redirect('/action', code=302)
        else:
            return redirect('/login_failed', code=302)
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
            return f'id {id} already exists try again'

        cur.execute("INSERT INTO users VALUES(%s, %s);", (id, password))
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
    return redirect('/', code=302)

############ main page ############

def user_info():
    cur.execute("SELECT * FROM users;")
    result = cur.fetchall()
    return render_template('user_info.html', users=result)

def trade_info():
    return render_template('trade_info.html')

@app.route('/admin_func')
def admin_func():
    send = request.form["send"]
    if send == "user_info":
        return user_info()
    if send == 'trades_info':
        return render_template('trade_info.html')
    return "invalid request try again please"

@app.route("/action")
def action():
    id = session['id']
    return render_template(
        "action.html",
        admin_display='show' if id == 'admin' else 'none',
        id=id
    )
    # return render_template("main.html")


@app.route("/item_add")
def item_add():
    return render_template("main.html")


@app.route("/item_buy")
def item_buy():
    return render_template("main.html")


@app.route("/item_buying")
def item_buying():
    return render_template("main.html")


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, "static"), "favicon.ico", mimetype="image/vnd.microsoft.icon"
    )

if __name__ == "__main__":
    app.run()
