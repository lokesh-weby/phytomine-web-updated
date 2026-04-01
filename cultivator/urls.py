from django.urls import path
from .views import *


urlpatterns = [
    path("cul_login/",cul_login),
    path("cul_logout/",cul_logout),
    path("cul_reg/",cul_reg),
    path("cul_home/", cul_home),
    path("cul_validate_login/", cul_validate_login),
    path("cul_req/",cul_req),
    path('getkey_cul/<str:project_id>/', getkey_cul, name='getkey_cul'),
    path('decrypt_cul/<str:project_id>/', decrypt_cul, name='decrypt_data_cul'),
    path("cul_ana/",cul_ana),
    path("cul_ana_process/<str:project_id>/",cul_ana_process),
    path("cul_rep/",cul_rep),
]