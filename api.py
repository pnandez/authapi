from flask import Flask, request, abort, redirect
import sqlite3 as sql
from setup import User

db_name = "users"
db_fields = ["email", "password_hash", "admin"]
app = Flask(__name__)

db_connection = sql.connect("database.db")
db_cursor = db_connection.cursor()
if not sql.connect("databas.db"):
  os.system("createdb.py")

@app.route('/')
def a():
  return ''

@app.route('/user', methods = ["POST"])
def create_user():
  with sql.connect("database.db") as con:
    cur = con.cursor()
    print('HELLOOO')
    data = request.get_json()
    user = data['user']
    password = data['password']
    admin = "NO"

    if user is not None and password is not None:
      user1 = User(user, password, admin)
      cur.execute("INSERT INTO %s (%s, %s, %s) VALUES ('%s', '%s', '%s')" %(db_name, db_fields[0], db_fields[1], db_fields[2], user1.user, user1.passwd_hash, user1.admin))
      con.commit()

      return "User %s saved"  % user1.user
    else:

      return "ERRORRR"


@app.route('/user', methods=["GET"])
def get_users():
  with sql.connect("database.db") as con:
    cur = con.cursor()
    cur.execute("SELECT * from users")
    records = cur.fetchall()
    str = ''
    for row in records:
      str = str + row[0] + "\t" + row[1] + "\t" + row[2] + "\n"
    return str


@app.route('/user/<username>', methods=["DELETE"])
def del_users(username):
#implement search first for user(error handling)
  with sql.connect("database.db") as con:
    cur = con.cursor()
    cur.execute("DELETE from users WHERE email LIKE '%s'" % username)
    
    return redirect("/user")




if __name__ == '__main__':
  app.run(debug=True)
