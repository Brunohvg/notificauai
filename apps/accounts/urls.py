from django.urls import path
from apps.accounts.views.auth import (
    login_view,
    register_view,
    logout_view,
    password_reset_request_view,
    password_reset_confirm_view,
    # activate_account_view,  # se tiver essa view, descomenta
    # account_detail_view,
    # current_user_view,
)

app_name = 'accounts'

urlpatterns = [
    path('login/', login_view, name='login'),                      # /accounts/login/
    path('logout/', logout_view, name='logout'),                   # /accounts/logout/
    path('register/', register_view, name='register'),             # /accounts/register/

    path('password-reset/', password_reset_request_view, name='password-reset'),  # /accounts/password-reset/
    path(
    'password-reset-confirm/<str:uidb64>/<str:token>/',
    password_reset_confirm_view,
    name='password-reset-confirm'
)
    #path('password-reset-confirm/<str:uid>/<str:token>/', password_reset_confirm_view, name='password-reset-confirm'),  # /accounts/password-reset-confirm/{uid}/{token}/

    # Descomente essas abaixo se tiver implementado:
    # path('<int:id>/', account_detail_view, name='detail'),       # /accounts/{id}/
    # path('me/', current_user_view, name='me'),                   # /accounts/me/
    # path('activate/<str:token>/', activate_account_view, name='activate'),  # /accounts/activate/{token}/
]
