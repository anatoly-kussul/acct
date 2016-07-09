from views import MainView, LoginView, SignInView, LogOutView, AddVisitorView

routes = [
    ('GET', '/', MainView, 'main'),
    ('*', '/login', LoginView, 'login'),
    ('*', '/logout', LogOutView, 'logout'),
    ('*', '/sign', SignInView, 'sign'),
    ('*', '/add_visitor', AddVisitorView, 'add_visitor'),
]
