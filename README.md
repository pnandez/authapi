# authapi
User-password authorization RESTful API on flask with JWT

# Installation
Use pyhton´s pip package manager to install all the dependencies in requirements.txt
```bash
pip install -r requirements.txt
```

# Usage
First run the api with
```bash
python api.py
```
After that, you can make http requests to the IP where it is running:

"/userinfo", method = GET: Returns all the users with their information in a json object.
"/useradd", method = POST: Creates a new user. In the body a "username" and a "password" must be send in a json object.
"/delete_user/<username>" or "/user/<username>", method = DELETE: Deletes the username given in the url.
"/user/<username>", method  = GET: Returns in a json object the information of the user <username>.
"/login", method = POST: Returns a JWT, for authentication on some of the other routes, if credentials are correct. Credentials must be sent in the body inside a json object as "username" and "password".

All of the routes return a JSON object formatted as follows:
```bash
{
  "http_status": ,
  "info": ,
}
´´´