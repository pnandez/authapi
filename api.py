from flask import Flask, request, abort, redirect, render_template, jsonify, make_response
import sqlite3 as sql
from setup import User
from flask_jwt_extended import JWTManager

db_name = "users"
db_fields = ["email", "password_hash", "admin"]
app = Flask(__name__)
app.config.from_envvar('ENV_FILE_LOCATION')
jwt = JWTManager(app)

msg = ''

db_connection = sql.connect("database.db")
db_cursor = db_connection.cursor()
if not sql.connect("databas.db"):
  os.system("createdb.py")


#Page to display a table with al the users and if they are admin or not
@app.route('/userinfo', methods=["GET"])
def user_display_admin():
  with sql.connect("database.db") as con:
   cur = con.cursor()
   cur.execute("SELECT * from users")
   records = cur.fetchall()
   users = []
   for record in records:
     users.append(dict(username=record[0], admin=record[-1]))
  return render_template("user_info.html", users=users)





#Form to add a new user to the database
@app.route('/useradd', methods=["GET", "POST"])
def user_form():
  if request.method == "POST":
    global msg
    user = User(request.form["username"], request.form["passwd"])
    if request.form.getlist("admin"):
      user.admin = "YES"
    with sql.connect("database.db") as con:
      cur = con.cursor()
      cur.execute("SELECT EXISTS(SELECT * FROM users WHERE email LIKE '%s')" % user.user)
      users_list = cur.fetchone()
      if users_list is not None:
        msg = "Usuario existente."
        return redirect("userinfo")
      else:
        cur.execute("INSERT INTO %s (%s, %s, %s) VALUES ('%s', '%s', '%s')" % (db_name, db_fields[0], db_fields[1], db_fields[2], user.user, user.passwd, user.admin))
        con.commit()
        msg = "Usuario creado correctamente."
        return redirect("/userinfo")
  else:
    return render_template("new_user.html")



#Get information of a certain user
@app.route('/user/<username>', methods=["GET"])
def get_users(username):
  with sql.connect("database.db") as con:
    cur = con.cursor()
    cur.execute("SELECT * from users WHERE email like '%s'" % username)
    records = cur.fetchall()
    if records:
      user = User(records[0][0], records[0][1], records[0][2])
      return user.user + user.passwd + user.admin
    else:
      return "User doesn´t exist"


@app.route('/user/<username>', methods=["DELETE"])
def del_users(username):
#TODO implement search first for user(error handling)
  with sql.connect("database.db") as con:
    cur = con.cursor()
    cur.execute("DELETE from users WHERE email LIKE '%s'" % username)
    
    return redirect("/user")


@app.route("/login")
def login():
  data = request.get_json()
  username = data['user']
  password_given = data['password']
  with sql.connect("database.db") as con:
    cur = con.cursor()
    cur.execute("SELECT * from users WHERE email like '%s'" % username)
    records = cur.fetchall()
    if records: #If the user exists
      user = User(records[0][0], records[0][1], records[0][2])
      if user.verify_passwd(password=password_given):
        return "YAYY"
    else:
      #TODO implement error handling if user doesn´t exist
      return ''


if __name__ == '__main__':
  app.run(debug=True)
