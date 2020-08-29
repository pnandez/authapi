from flask import Flask, request, abort, redirect, render_template, jsonify, make_response
import sqlite3 as sql
import jwt
import datetime
import json
from functools import wraps


app = Flask(__name__)
app.config["SECRET_KEY"] = "Escultism0"


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
      return jsonify({
        "http_status": 400,
        "info": "Token not provided",
        })

    try:
      data = jwt.decode(token, app.config["SECRET_KEY"])
      user = db.get_one(db_table, db_fields[0], data[token_fields[0]])
      current_user = User(user[0][0], password='', admin=user[0][2])
      current_user.passwd = user[0][1]
    except:
      return jsonify({
          "http_status": 401,
          "info": "Invalid token",
      })
    return f(current_user, *args, **kwargs)
  return decorated


#Page to display a table with al the users and if they are admin or not
@app.route('/userinfo', methods=["GET"])
@token_required
def user_display_admin(current_user):
  """ if current_user.admin == "NO":
    return jsonify({
        "http_status": 401,
        "info": "Usuario no autorizado",
    }) """
  records = db.get_all("users")
  users = []
  for record in records:
    users.append(dict(username=record[0], passwd=record[1], admin=record[-1]))
  return jsonify({
      "http_status": 200,
      "Usuarios": users,
  })

  #WORKS





#Form to add a new user to the database
@app.route('/useradd', methods=["POST"])
def user_form():
  if request.method == "POST":
    data = request.get_json()

    user = User(user=data["username"], password=data["password"])
    if request.get_json("admin"):
      user.admin = "YES"
    if db.exists(db_table, db_fields[0], user.user):
      return jsonify({
          "http_status": 405,
          "info": "User already exists"
      })
    else:
      if db.insert(db_table, db_fields, user):
        return jsonify({
          "http_status": 200 ,
          "info": "User created" 
        })
      else:
        return jsonify({
            "http_status": 500,
            "info": "User not created"
        })
#WORKS


@app.route('/delete_user/<username>', methods=["DELETE"])
def delusers(username):
  if db.exists(db_table, db_fields[0], username):
    db.delete(db_table, db_fields[0], username)
    return jsonify({
        "http_status": 200,
        "Deleted users": "User %s deleted" % username,
    })
  else:
    return jsonify({
        "http_status": 410,
        "info" : "User doesn´t exist",
    })

#Get information of a certain user
@app.route('/user/<username>', methods=["GET"])
def get_users(username):
  records = db.get_one( table="users", column="email", data=username)
  if records:
    user = User(records[0][0], records[0][1], records[0][2])
    info = {
        "username": user.user,
        "admin": user.admin
    }
    return jsonify(
        {
            "http_status": 200 ,
            "info": info,
        }
    )
  else:
    return jsonify({
        "http_status": 410,
        "info": "User doesn´t exist" ,
    })


@app.route('/user/<username>', methods=["DELETE"])
def del_users(username):
#TODO implement search first for user(error handling)
  if db.delete(db_table, db_fields[0], username):
    return jsonify({"Message" : "User deleted"})
  else:
    return jsonify({"Message": "User not deleted"})


@app.route("/login", methods=["POST"])
def login():
  data = request.get_json()
  if not data:
    return jsonify({
        "http_status": 400,
        "info": "Please provide user and password",
    })
  username = data['username']
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
      return jsonify({
          "http_status": 400,
          "info": "Incorrect password",
      })
  else:
    return jsonify({
        "http_status": 410,
        "info": "User not found",
    })


@app.route("/checktoken")
@token_required
def checktoken(current_user):
  return json.dumps("True")

if __name__ == '__main__':
  app.run(debug=True)
