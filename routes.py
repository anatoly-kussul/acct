from views import MainView, LoginView, SignInView, LogOutView, AddVisitorView, RemoveVisitorView, DischargeView

routes = [
    ('GET', '/', MainView, 'main'),
    ('*', '/login', LoginView, 'login'),
    ('*', '/logout', LogOutView, 'logout'),
    ('*', '/sign', SignInView, 'sign'),
    ('*', '/add_visitor', AddVisitorView, 'add_visitor'),
    ('*', '/remove_visitor', RemoveVisitorView, 'remove_visitor'),
    ('*', '/discharge', DischargeView, 'discharge'),
]
