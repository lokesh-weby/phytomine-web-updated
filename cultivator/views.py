from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from admins.models import *

# Create your views here.

def cul_home(request):
    if request.session.get('department') != "CULTIVATOR":
        messages.error(request, "Unauthorized Access")
        return redirect("/cul_login/")

    return render(request,'cul/cul_home.html')

def cul_login(request):
    return render(request,'cul/cul_login.html')

def cul_reg(request):
    if request.method =='POST':
        name=request.POST['name']
        email=request.POST['email']
        mobile_no=request.POST['mobile_no']
        department=request.POST['department']
        registration(name=name,email=email,mobile_no=mobile_no,department=department).save()
        messages.info(request,"CULTIVATOR Registration successful")
        return redirect('/cul_reg/')
    else:
        return render(request,"cul/cul_login.html")
    
def cul_validate_login(request):
    if request.method=='POST':
        
        email = request.POST['email']
        password = request.POST['password']
        try:        
            data = registration.objects.get(email=email, password=password, department="CULTIVATOR")
            if data.accept:   
                data.login = True
                data.logout = False
                data.save()

                # Store all three safely
                request.session['user_id'] = data.id
                request.session['email'] = data.email
                request.session['department'] = data.department

                messages.info(request, "CULTIVATOR Login Successful")     
                return redirect("/cul_home/")
            else:
                messages.info(request, "Wrong Credentials")
                return redirect("/cul_login/")
        except:
            messages.info(request, "Wrong Credentials")
            return redirect("/cul_login/")
    return render(request, "cul/cul_login.html")


def cul_logout(request):
    user_id = request.session.get('user_id')
    email = request.session.get('email')
    department = request.session.get('department')

    if user_id and department:
        
        try:
            data = registration.objects.get(id=user_id, department=department, email=email)
            data.login = False
            data.logout = True
            
            data.save()
        except registration.DoesNotExist:
            
            pass

    # Clear all session data
    request.session.flush()

    messages.info (request,"CULTIVATOR Logout Successfull")
    return redirect("/")

from django.shortcuts import get_object_or_404, render, redirect
from django.core.mail import send_mail
from django.contrib import messages


from .crypto_utils import encrypt_data, decrypt_data, generate_token, verify_token


def cul_req(request):
    if request.session.get('department') != "CULTIVATOR":
        messages.error(request, "Unauthorized Access")
        return redirect("/cul_login/")

    data = phytomine.objects.all()

    for item in data:
        if not item.e_initial_fern_biomass:
            item.e_initial_fern_biomass = encrypt_data(str(item.initial_fern_biomass or ""))
        if not item.e_final_fern_biomass:
            item.e_final_fern_biomass = encrypt_data(str(item.final_fern_biomass or ""))
        if not item.e_growth_duration:
            item.e_growth_duration = encrypt_data(str(item.growth_duration or ""))
        if not item.e_soil_ree_conc:
            item.e_soil_ree_conc = encrypt_data(str(item.soil_ree_conc or ""))
        if not item.e_plant_ree_conc:
            item.e_plant_ree_conc = encrypt_data(str(item.plant_ree_conc or ""))
        if not item.e_harvested_biomass:
            item.e_harvested_biomass = encrypt_data(str(item.harvested_biomass or ""))
        if not item.e_extraction_eff:
            item.e_extraction_eff = encrypt_data(str(item.extraction_eff or ""))
        if not item.e_initial_soil_ree:
            item.e_initial_soil_ree = encrypt_data(str(item.initial_soil_ree or ""))
        if not item.e_final_soil_ree:
            item.e_final_soil_ree = encrypt_data(str(item.final_soil_ree or ""))

        item.save()

    return render(request, "cul/cul_req.html", {"data": data})

def getkey_cul(request, project_id):
    if request.session.get('department') != "CULTIVATOR":
        messages.error(request, "Unauthorized Access")
        return redirect("/cul_login/")

    data = get_object_or_404(phytomine, project_id=project_id)
    reg_obj = get_object_or_404(registration, login=True, logout=False, department="CULTIVATOR")

    token = generate_token(data.pk)

    data.cul_decrypt_key = token
    data.cul_get_key = True
    data.save()

    send_mail(
        "CULTIVATOR: Secure Decryption Token",
        f"Project ID: {data.project_id}\n\nYour Secure Token:\n{token}",
        settings.EMAIL_HOST_USER,
        [reg_obj.email],
        fail_silently=False,
    )

    messages.success(request, "Secure decryption key sent successfully")
    return redirect("/cul_req/")

def decrypt_cul(request, project_id):
    if request.session.get('department') != "CULTIVATOR":
        messages.error(request, "Unauthorized Access")
        return redirect("/cul_login/")

    d = get_object_or_404(phytomine, project_id=project_id)

    if request.method == "POST":
        token = request.POST.get("decryption_key", "").strip()

        try:
            if verify_token(token, d.pk):
                d.cul_decrypt = True
                # Digitally sign by storing user name
                user_id = request.session.get('user_id')
                if user_id:
                    try:
                        u = registration.objects.get(id=user_id)
                        d.cul_signed_by = u.name
                    except registration.DoesNotExist:
                        pass
                d.save()
                messages.success(request, f"{project_id}: Decryption Verified ✅")
            else:
                messages.error(request, f"{project_id}: Invalid or Expired Token ❌")

        except Exception as e:
            messages.error(request, f"Error: {str(e)}")

    return redirect("/cul_req/")

def cul_ana(request):
    if request.session.get('department') != "CULTIVATOR":
        messages.error(request, "Unauthorized Access")
        return redirect("/cul_login/")

    data = phytomine.objects.all()
    return render(request, "cul/cul_ana.html", {"data": data})

def cul_ana_process(request, project_id):
    if request.session.get('department') != "CULTIVATOR":
        messages.error(request, "Unauthorized Access")
        return redirect("/cul_login/")


    data= phytomine.objects.get(project_id=project_id)

    biomass_increase = data.final_fern_biomass - data.initial_fern_biomass
    growth_rate = biomass_increase / data.growth_duration
    growth_eff = (biomass_increase / data.final_fern_biomass) * 100

    data.biomass_increase = round(biomass_increase, 3)
    data.growth_rate = round(growth_rate, 3)
    data.growth_eff = round(growth_eff, 3)

    data.cul_scan = True
    data.status = "CULTIVATOR Analysis Completed"
    data.save()

    messages.info(request,"CULTIVATOR Analysis Completed")
    return redirect("/cul_ana/")

def cul_rep(request):
    if request.session.get('department') != "CULTIVATOR":
        messages.error(request, "Unauthorized Access")
        return redirect("/cul_login/")

    data = phytomine.objects.all()
    return render(request, "cul/cul_rep.html", {"data": data})
