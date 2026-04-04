from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("",home),
     path("chat/", chatbot, name="chatbot"),
    path("admins_login/",admins_login),
    path("admins_home/",admins_home),
    path("admins_logout/",admins_logout),
    path("cul_approve/",cul_approve),
    path("acc_approve/",acc_approve),
    path("ext_approve/",ext_approve),
    path("sus_approve/",sus_approve),
    path("accept/<int:id>/",accept),
    path("reject/<int:id>/",reject),
    path("admins_req/",admins_req),
    path("admins_status/",admins_status),
    path("rep_cul/",rep_cul),
    path("rep_acc/",rep_acc),
    path("rep_ext/",rep_ext),
    path("rep_sus/",rep_sus),
    path("phytomine_generate_pdf/<str:project_id>/",phytomine_generate_pdf),
    path("download_report/<str:project_id>/", download_report),
    path("get_location_proxy/", get_location_proxy),
    path("predict_soil_type_ajax/", predict_soil_type_ajax),
    path("phytomine_dashboard/<str:project_id>/", phytomine_dashboard),
]

urlpatterns += static(settings.MEDIA_URL,document_root=settings
                      .MEDIA_ROOT)