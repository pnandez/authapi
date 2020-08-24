from passlib.apps import custom_app_context as pwd_context
from passlib.context import CryptContext
from flask_jwt_extended import create_access_token
import sqlite3 as sql



pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    default="pbkdf2_sha256",
    pbkdf2_sha256__default_rounds=30000
)

class User:
  def __init__(self, user, password, admin="NO"):
    self.user = user
    self.hash_passwd(password)
    self.admin = admin
    
    
  def hash_passwd(self, password):
    self.passwd = pwd_context.encrypt(password)

  def verify_passwd(self, password):
    return pwd_context.verify(password, self.passwd)

class DB:
  def __init__(self, database):
    self.database = database


  def get_all(self, table):
    with sql.connect("database.db") as con:
      cur = con.cursor()
      cur.execute("SELECT * from %s" % table)
      return cur.fetchall()


  def get_one(self, table,  column, data):
    with sql.connect(self.database) as con:
      cur = con.cursor()
      cur.execute("SELECT * from %s WHERE %s LIKE '%s'" % (table, column, data))
      records = cur.fetchall()
      return records
  
  def delete(self, table, column, data):
    if self.exists( table, column, data):
      with sql.connect(self.database) as con:
        cur = con.cursor()
        cur.execute("DELETE from %s WHERE %s LIKE '%s'" % (table, column, data))
        return True

  def exists(self, table, column, data):
    with sql.connect(self.database) as con:
      cur = con.cursor()
      cur.execute("SELECT * FROM %s WHERE (EXISTS(SELECT 1 FROM %s WHERE %s='%s'))" % (table,table, column, data))
      if cur.fetchone():
        return True
      else:
        return False
  
  def insert(self, table, table_columns, data):
    with sql.connect(self.database) as con:
      cur = con.cursor()
      cur.execute("INSERT INTO %s (%s, %s, %s) VALUES ('%s', '%s', '%s')" % (table, table_columns[0], table_columns[1], table_columns[2], data.user, data.passwd, data.admin))
      con.commit()
      return True
