from flask import Flask, request, abort, redirect, render_template, jsonify, make_response
import sqlite3 as sql
from setup import User, DB
from flask_jwt_extended import JWTManager

app = Flask(__name__)
app.config.from_envvar('ENV_FILE_LOCATION')

db_table = "users"
db_fields = ["email", "password_hash", "admin"]
database = "database.db"
jwt = JWTManager(app)

db = DB(database)
if not sql.connect(database):
  os.system("createdb.py")


#Page to display a table with al the users and if they are admin or not
@app.route('/userinfo', methods=["GET"])
def user_display_admin():
  records = db.get_all("users")
  users = []
  for record in records:
    users.append(dict(username=record[0], admin=record[-1]))
  return render_template("user_info.html", users=users)

  #WORKS





#Form to add a new user to the database
@app.route('/useradd', methods=["GET", "POST"])
def user_form():
  if request.method == "POST":
    global msg
    user = User(request.form["username"], request.form["passwd"])
    if request.form.getlist("admin"):
      user.admin = "YES"
    if db.exists(db_table, db_fields[0], user.user):
      return redirect("userinfo")
    else:
      if db.insert(db_table, db_fields, user):
        return redirect("userinfo")
      else:
        return jsonify({"Message" : "User not created"})
  else:
    return render_template("new_user.html")



#Get information of a certain user
@app.route('/user/<username>', methods=["GET"])
def get_users(username):
  records = db.search( table="users", column="email", data=username)
  if records:
    user = User(records[0][0], records[0][1], records[0][2])
    return user.user + "\t " + user.passwd + "\t" + user.admin
  else:
    return "User doesn´t exist"


@app.route('/user/<username>', methods=["DELETE"])
def del_users(username):
#TODO implement search first for user(error handling)
  if db.delete(db_table, db_fields[0], username):
    return jsonify({"Message" : "User deleted"})
  else:
    return jsonify({"Message": "User not deleted"})

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
        user.get_token()
        return 
    else:
      #TODO implement error handling if user doesn´t exist
      return ''


if __name__ == '__main__':
  app.run(debug=True)
