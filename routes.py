from views import MainView, LoginView, SignInView, LogOutView

routes = [
    ('GET', '/', MainView, 'main'),
    ('*', '/login', LoginView, 'login'),
    ('*', '/logout', LogOutView, 'logout'),
    ('*', '/sign', SignInView, 'sign'),
]
