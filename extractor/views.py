from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from admins.models import *

# Create your views here.

def ext_home(request):
    if request.session.get('department') != "EXTRACTOR":
        messages.error(request, "Unauthorized Access")
        return redirect("/ext_login/")

    return render(request,'ext/ext_home.html')

def ext_login(request):
    return render(request,'ext/ext_login.html')

def ext_reg(request):
    if request.method =='POST':
        name=request.POST['name']
        email=request.POST['email']
        mobile_no=request.POST['mobile_no']
        department=request.POST['department']
        registration(name=name,email=email,mobile_no=mobile_no,department=department).save()
        messages.info(request,"EXTRACTOR Registration successful")
        return redirect('/ext_reg/')
    else:
        return render(request,"ext/ext_login.html")
    
def ext_validate_login(request):
    if request.method=='POST':
        
        email = request.POST['email']
        password = request.POST['password']
        try:        
            data = registration.objects.get(email=email, password=password, department="EXTRACTOR")
            if data.accept:   
                data.login = True
                data.logout = False
                data.save()

                # Store all safely
                request.session['user_id'] = data.id
                request.session['email'] = data.email
                request.session['department'] = data.department
                request.session['name'] = data.name

                messages.info(request, "EXTRACTOR Login Successful")     
                return redirect("/ext_home/")
            else:
                messages.info(request, "Wrong Credentials")
                return redirect("/ext_login/")
        except:
            messages.info(request, "Wrong Credentials")
            return redirect("/ext_login/")
    return render(request, "ext/ext_login.html")


def ext_logout(request):
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

    messages.info (request,"EXTRACTOR Logout Successfull")
    return redirect("/")

from django.shortcuts import get_object_or_404, render, redirect
from django.core.mail import send_mail
from django.contrib import messages


from .crypto_utils import encrypt_data, decrypt_data, generate_token, verify_token


def ext_req(request):
    if request.session.get('department') != "EXTRACTOR":
        messages.error(request, "Unauthorized Access")
        return redirect("/ext_login/")

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
        if not item.e_biomass_increase:
            item.e_biomass_increase = encrypt_data(str(item.biomass_increase or ""))
        if not item.e_growth_rate:
            item.e_growth_rate = encrypt_data(str(item.growth_rate or ""))
        if not item.e_growth_eff:
            item.e_growth_eff = encrypt_data(str(item.growth_eff or ""))
        if not item.e_total_metal:
            item.e_total_metal = encrypt_data(str(item.total_metal or ""))
        if not item.e_uptake:
            item.e_uptake = encrypt_data(str(item.uptake or ""))
        if not item.e_baf:
            item.e_baf = encrypt_data(str(item.baf or ""))

        item.save()

    return render(request, "ext/ext_req.html", {"data": data})

def getkey_ext(request, project_id):
    if request.session.get('department') != "EXTRACTOR":
        messages.error(request, "Unauthorized Access")
        return redirect("/ext_login/")

    data = get_object_or_404(phytomine, project_id=project_id)
    reg_obj = get_object_or_404(registration, login=True, logout=False, department="EXTRACTOR")

    token = generate_token(data.pk)

    data.ext_decrypt_key = token
    data.ext_get_key = True
    data.save()

    send_mail(
        "EXTRACTOR: Secure Decryption Token",
        f"Project ID: {data.project_id}\n\nYour Secure Token:\n{token}",
        settings.EMAIL_HOST_USER,
        [reg_obj.email],
        fail_silently=False,
    )

    messages.success(request, "Secure decryption key sent successfully")
    return redirect("/ext_req/")

def decrypt_ext(request, project_id):
    if request.session.get('department') != "EXTRACTOR":
        messages.error(request, "Unauthorized Access")
        return redirect("/ext_login/")

    d = get_object_or_404(phytomine, project_id=project_id)

    if request.method == "POST":
        token = request.POST.get("decryption_key", "").strip()

        try:
            if verify_token(token, d.pk):
                d.ext_decrypt = True
                # Digitally sign by storing user name
                user_id = request.session.get('user_id')
                if user_id:
                    try:
                        u = registration.objects.get(id=user_id)
                        d.ext_signed_by = u.name
                    except registration.DoesNotExist:
                        pass
                d.save()
                messages.success(request, f"{project_id}: Decryption Verified ✅")
            else:
                messages.error(request, f"{project_id}: Invalid or Expired Token ❌")

        except Exception as e:
            messages.error(request, f"Error: {str(e)}")

    return redirect("/ext_req/")

def ext_ana(request):
    if request.session.get('department') != "EXTRACTOR":
        messages.error(request, "Unauthorized Access")
        return redirect("/ext_login/")

    data = phytomine.objects.all()
    return render(request, "ext/ext_ana.html", {"data": data})

def ext_ana_process(request, project_id):
    if request.session.get('department') != "EXTRACTOR":
        messages.error(request, "Unauthorized Access")
        return redirect("/ext_login/")


    data= phytomine.objects.get(project_id=project_id)

    recovered_metal = (data.total_metal * (data.extraction_eff / 100))
    loss = data.total_metal - recovered_metal
    recovery = data.extraction_eff

    data.recovered_metal = round(recovered_metal, 3)
    data.loss = round(loss, 3)
    data.recovery = round(recovery, 3)
    data.ext_scan = True
    data.status = "EXTRACTOR Analysis Completed"
    data.save()

    messages.info(request,"EXTRACTOR Analysis Completed")
    return redirect("/ext_ana/")

def ext_rep(request):
    if request.session.get('department') != "EXTRACTOR":
        messages.error(request, "Unauthorized Access")
        return redirect("/ext_login/")

    data = phytomine.objects.all()
    return render(request, "ext/ext_rep.html", {"data": data})