from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from admins.models import *

# Create your views here.

def acc_home(request):
    if request.session.get('department') != "ACCUMULATOR":
        messages.error(request, "Unauthorized Access")
        return redirect("/acc_login/")

    return render(request,'acc/acc_home.html')

def acc_login(request):
    return render(request,'acc/acc_login.html')

def acc_reg(request):
    if request.method =='POST':
        name=request.POST['name']
        email=request.POST['email']
        mobile_no=request.POST['mobile_no']
        department=request.POST['department']
        registration(name=name,email=email,mobile_no=mobile_no,department=department).save()
        messages.info(request,"ACCUMULATOR Registration successful")
        return redirect('/acc_reg/')
    else:
        return render(request,"acc/acc_login.html")
    
def acc_validate_login(request):
    if request.method=='POST':
        
        email = request.POST['email']
        password = request.POST['password']
        try:        
            data = registration.objects.get(email=email, password=password, department="ACCUMULATOR")
            if data.accept:   
                data.login = True
                data.logout = False
                data.save()

                # Store all three safely
                request.session['user_id'] = data.id
                request.session['email'] = data.email
                request.session['department'] = data.department

                messages.info(request, "ACCUMULATOR Login Successful")     
                return redirect("/acc_home/")
            else:
                messages.info(request, "Wrong Credentials")
                return redirect("/acc_login/")
        except:
            messages.info(request, "Wrong Credentials")
            return redirect("/acc_login/")
    return render(request, "acc/acc_login.html")


def acc_logout(request):
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

    messages.info (request,"ACCUMULATOR Logout Successfull")
    return redirect("/")

from django.shortcuts import get_object_or_404, render, redirect
from django.core.mail import send_mail
from django.contrib import messages


from .crypto_utils import encrypt_data, decrypt_data, generate_token, verify_token


def acc_req(request):
    if request.session.get('department') != "ACCUMULATOR":
        messages.error(request, "Unauthorized Access")
        return redirect("/acc_login/")

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

        item.save()

    return render(request, "acc/acc_req.html", {"data": data})

def getkey_acc(request, project_id):
    if request.session.get('department') != "ACCUMULATOR":
        messages.error(request, "Unauthorized Access")
        return redirect("/acc_login/")

    data = get_object_or_404(phytomine, project_id=project_id)
    reg_obj = get_object_or_404(registration, login=True, logout=False, department="ACCUMULATOR")

    token = generate_token(data.pk)

    data.acc_decrypt_key = token
    data.acc_get_key = True
    data.save()

    send_mail(
        "ACCUMULATOR: Secure Decryption Token",
        f"Project ID: {data.project_id}\n\nYour Secure Token:\n{token}",
        settings.EMAIL_HOST_USER,
        [reg_obj.email],
        fail_silently=False,
    )

    messages.success(request, "Secure decryption key sent successfully")
    return redirect("/acc_req/")

def decrypt_acc(request, project_id):
    if request.session.get('department') != "ACCUMULATOR":
        messages.error(request, "Unauthorized Access")
        return redirect("/acc_login/")

    d = get_object_or_404(phytomine, project_id=project_id)

    if request.method == "POST":
        token = request.POST.get("decryption_key", "").strip()

        try:
            if verify_token(token, d.pk):
                d.acc_decrypt = True
                # Digitally sign by storing user name
                user_id = request.session.get('user_id')
                if user_id:
                    try:
                        u = registration.objects.get(id=user_id)
                        d.acc_signed_by = u.name
                    except registration.DoesNotExist:
                        pass
                d.save()
                messages.success(request, f"{project_id}: Decryption Verified ✅")
            else:
                messages.error(request, f"{project_id}: Invalid or Expired Token ❌")

        except Exception as e:
            messages.error(request, f"Error: {str(e)}")

    return redirect("/acc_req/")

def acc_ana(request):
    if request.session.get('department') != "ACCUMULATOR":
        messages.error(request, "Unauthorized Access")
        return redirect("/acc_login/")

    data = phytomine.objects.all()
    return render(request, "acc/acc_ana.html", {"data": data})

def acc_ana_process(request, project_id):
    if request.session.get('department') != "ACCUMULATOR":
        messages.error(request, "Unauthorized Access")
        return redirect("/acc_login/")


    data= phytomine.objects.get(project_id=project_id)

    total_metal = ((data.plant_ree_conc * data.harvested_biomass) / 1000)
    uptake = (data.plant_ree_conc / data.soil_ree_conc) * 100
    baf = (data.plant_ree_conc / data.soil_ree_conc)

    data.total_metal = round(total_metal, 3)
    data.uptake = round(uptake, 3)
    data.baf = round(baf, 3)

    data.acc_scan = True
    data.status = "ACCUMULATOR Analysis Completed"
    data.save() 

    messages.info(request,"ACCUMULATOR Analysis Completed")
    return redirect("/acc_ana/")

def acc_rep(request):
    if request.session.get('department') != "ACCUMULATOR":
        messages.error(request, "Unauthorized Access")
        return redirect("/acc_login/")

    data = phytomine.objects.all()
    return render(request, "acc/acc_rep.html", {"data": data})