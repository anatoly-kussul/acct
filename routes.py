from views import (
    MainView,
    LoginView,
    SignInView,
    CloseShiftView,
    AddVisitorView,
    RemoveVisitorView,
    DischargeView,
    StaticsView,
)

routes = [
    ('GET', '/', MainView, 'main'),
    ('*', '/login', LoginView, 'login'),
    ('*', '/close_shift', CloseShiftView, 'logout'),
    ('*', '/sign', SignInView, 'sign'),
    ('*', '/add_visitor', AddVisitorView, 'add_visitor'),
    ('*', '/remove_visitor', RemoveVisitorView, 'remove_visitor'),
    ('*', '/discharge', DischargeView, 'discharge'),
    ('*', '/statistics', StaticsView, 'statistics'),
]
