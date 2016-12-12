from eblank.views import (
    MainView,
    LoginView,
    RegisterView,
    CloseShiftView,
    AddVisitorView,
    RemoveVisitorView,
    DischargeView,
    StaticsView,
    ShiftInfoView
)

routes = [
    ('GET', '/', MainView, 'main'),
    ('*', '/login', LoginView, 'login'),
    ('*', '/close_shift', CloseShiftView, 'logout'),
    ('*', '/register', RegisterView, 'register'),
    ('*', '/add_visitor', AddVisitorView, 'add_visitor'),
    ('*', '/remove_visitor', RemoveVisitorView, 'remove_visitor'),
    ('*', '/discharge', DischargeView, 'discharge'),
    ('*', '/statistics', StaticsView, 'statistics'),
    ('*', '/shift_info', ShiftInfoView, 'shift_info'),
]
