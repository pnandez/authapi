from flask import Flask, request, abort, redirect, render_template, jsonify, make_response
import sqlite3 as sql
import jwt
import datetime
from flask_bcrypt import Bcrypt
from functools import wraps


app = Flask(__name__)
app.config["SECRET_KEY"] = "Escultism0"

bcrypt = Bcrypt(app)


db_table = "users"
db_fields = ["email", "password_hash", "admin"]
database = "database.db"

token_fields = ["email"]

from setup import User, DB
db = DB(database)
if not sql.connect(database):
  os.system("createdb.py")


def token_required(f):
  @wraps(f)
  def decorated(*args, **kwargs):
    token = None

    if 'access_token' in request.headers:
      token = request.headers['access_token']
    
    if not token:
      return make_response("No token provided", 400)

    try:
      data = jwt.decode(token, app.config["SECRET_KEY"])
      user = db.get_one(db_table, db_fields[0], data[token_fields[0]])
      print (user[0][0])
      current_user = User(user[0][0], password='', admin=user[0][2])
      print ("A\n")
      current_user.passwd = user[0][1]
    except:
      return make_response("Invalid token", 401)
    return f(current_user, *args, **kwargs)
  return decorated


#Page to display a table with al the users and if they are admin or not
@app.route('/userinfo', methods=["GET"])
@token_required
def user_display_admin(current_user):
  if current_user.admin == "NO":
    return make_response("Only available for admin users", 401)
  records = db.get_all("users")
  users = []
  for record in records:
    users.append(dict(username=record[0], passwd=record[1], admin=record[-1]))
  return render_template("user_info.html", users=users)

  #WORKS





#Form to add a new user to the database
@app.route('/useradd', methods=["GET", "POST"])
def user_form():
  if request.method == "POST":
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
#WORKS


@app.route('/delete_users', methods=["GET", "POST"])
def delusers():
  if request.method == "POST":
    users_to_delete = request.form.getlist("delete_users")
    for user in users_to_delete:
      db.delete(db_table, db_fields[0], user)
    return redirect('/userinfo')
  else:
    records = db.get_all("users")
    users = []
    for record in records:
      users.append(dict(username=record[0], passwd=record[1], admin=record[-1]))
    return render_template("delete_users.html", users=users)


#Get information of a certain user
@app.route('/user/<username>', methods=["GET"])
def get_users(username):
  records = db.get_one( table="users", column="email", data=username)
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


@app.route("/login", methods=["POST"])
def login():
  data = request.get_json()
  if not data:
    return make_response("Please provide user and password", 400)
  username = data['user']
  password_given = data['password']
  records = db.get_one(db_table, db_fields[0], username)
  if records: #If the user exists
    user = User(records[0][0], records[0][1], records[0][2])
    user.passwd = records[0][1]
    print (user.passwd)
    if user.verify_passwd(password=password_given): #If passwd correct
      print("B")
      token = jwt.encode({token_fields[0] : user.user, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
      return jsonify({'token' : token.decode('UTF-8')})
    else:
      return make_response("Incorrect password", 401)
  else:
    return make_response("User not found", 401)


if __name__ == '__main__':
  app.run(debug=True)
