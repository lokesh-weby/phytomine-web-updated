from django.urls import path
from .views import *


urlpatterns = [
    path("ext_login/",ext_login),
    path("ext_logout/",ext_logout),
    path("ext_reg/",ext_reg),
    path("ext_home/", ext_home),
    path("ext_validate_login/", ext_validate_login),
    path("ext_req/",ext_req),
    path('getkey_ext/<str:project_id>/', getkey_ext, name='getkey_ext'),
    path('decrypt_ext/<str:project_id>/', decrypt_ext, name='decrypt_data_ext'),
    path("ext_ana/",ext_ana),
    path("ext_ana_process/<str:project_id>/",ext_ana_process),
    path("ext_rep/",ext_rep),
]