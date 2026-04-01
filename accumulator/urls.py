from django.urls import path
from .views import *


urlpatterns = [
    path("acc_login/",acc_login),
    path("acc_logout/",acc_logout),
    path("acc_reg/",acc_reg),
    path("acc_home/", acc_home),
    path("acc_validate_login/", acc_validate_login),
    path("acc_req/",acc_req),
    path('getkey_acc/<str:project_id>/', getkey_acc, name='getkey_acc'),
    path('decrypt_acc/<str:project_id>/', decrypt_acc, name='decrypt_data_acc'),
    path("acc_ana/",acc_ana),
    path("acc_ana_process/<str:project_id>/",acc_ana_process),
    path("acc_rep/",acc_rep),
]