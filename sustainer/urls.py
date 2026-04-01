from django.urls import path
from .views import *


urlpatterns = [
    path("sus_login/",sus_login),
    path("sus_logout/",sus_logout),
    path("sus_reg/",sus_reg),
    path("sus_home/", sus_home),
    path("sus_validate_login/", sus_validate_login),
    path("sus_req/",sus_req),
    path('getkey_sus/<str:project_id>/', getkey_sus, name='getkey_sus'),
    path('decrypt_sus/<str:project_id>/', decrypt_sus, name='decrypt_data_sus'),
    path("sus_ana/",sus_ana),
    path("sus_ana_process/<str:project_id>/",sus_ana_process),
    path("sus_rep/",sus_rep),
]