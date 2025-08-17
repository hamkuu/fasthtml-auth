from fasthtml import common as fh

app, rt = fh.fast_app()


@rt
def index():
    return fh.Div(fh.H1("Welcome to FastHTML"), fh.P("Hello, FastHTML!"))


fh.serve()
