from passlib.apps import custom_app_context as pwd_context

class User:
  def __init__(self, user, password, admin="NO"):
    self.user = user
    self.hash_passwd(password)
    self.admin = admin
    
    
  def hash_passwd(self, password):
    self.passwd = pwd_context.encrypt(password)

  def verify_passwd(self, password):
    return pwd_context.verify(password, self.passwd)