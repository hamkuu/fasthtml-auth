from fasthtml.common import *
from monsterui.all import *
from fasthtml.oauth import GoogleAppClient, OAuth
from fastlite import database
from starlette.responses import RedirectResponse

import os

app, rt = fast_app(hdrs=Theme.blue.headers(), live=True)


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
        return RedirectResponse("/home", status_code=303)


client = GoogleAppClient(os.getenv("GOOGLE_CLIENT_ID"), os.getenv("GOOGLE_CLIENT_SECRET"))
oauth = Auth(app, client, skip=("/", "/logout", "/redirect"), login_path="/")


def ex_navbar1():
    return NavBar(
        A("Home", href="/home"),
        A("Theme", href="/theme"),
        A("Logout", href="/logout"),
        brand=H3("FastHTML"),
    )


@rt
def index(req):
    return Center(
        DivVStacked(
            H1("Welcome"),
            A(UkIcon("log-in"), "Login with Google", href=oauth.login_link(req), cls=(ButtonT.primary, "btn")),
            Small(
                A(cls=AT.muted, href="#demo")("Terms of Service"),
                cls=(TextT.muted, "text-center"),
            ),
        ),
        cls="h-screen",
    )


@rt
def home(sess):
    user = db.users("oauth_id=?", (sess["auth"],))[0]
    return ex_navbar1(), Titled("Home", P(f"Welcome {user.email}"), A("Logout", href="/logout"))


@rt
def theme():
    return Container(
        DivVStacked(
            A(UkIcon("arrow-left"), "Back", href="javascript:history.back()", cls=(ButtonT.secondary, "btn")),
            ThemePicker(color=True, radii=True, shadows=True, font=True, mode=True, cls="p-4", custom_themes=[]),
        )
    )


serve()
