from fasthtml.common import *
from fasthtml.oauth import GoogleAppClient, OAuth
from fastlite import database
from starlette.responses import RedirectResponse

import os

app, rt = fast_app()


class User:
    id: int
    email: str
    oauth_id: str


db = database("database/fast_app.db")
db.users = db.create(User, transform=True)


class Auth(OAuth):
    def get_auth(self, info, ident, sess, state):
        sess["auth"] = info.sub
        user = db.users("oauth_id=?", (sess["auth"],))
        if not user:
            db.users.insert(User(oauth_id=sess["auth"], email=info.email))
        return RedirectResponse("/dashboard", status_code=303)


client = GoogleAppClient(os.getenv("GOOGLE_CLIENT_ID"), os.getenv("GOOGLE_CLIENT_SECRET"))
oauth = Auth(app, client, skip=("/", "/logout", "/redirect"), login_path="/")


@rt
def index(req):
    return Titled("FastHTML App", A("Login", href=oauth.login_link(req)))


@rt
def dashboard(sess):
    user = db.users("oauth_id=?", (sess["auth"],))[0]
    return Titled("Dashboard", P(f"Welcome back {user.email}"), A("Logout", href="/logout"))


serve()
