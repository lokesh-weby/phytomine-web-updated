from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from admins.models import *
import os

# Create your views here.

def sus_home(request):
    if request.session.get('department') != "SUSTAINER":
        messages.error(request, "Unauthorized Access")
        return redirect("/sus_login/")

    return render(request,'sus/sus_home.html')

def sus_login(request):
    return render(request,'sus/sus_login.html')

def sus_reg(request):
    if request.method =='POST':
        name=request.POST['name']
        email=request.POST['email']
        mobile_no=request.POST['mobile_no']
        department=request.POST['department']
        registration(name=name,email=email,mobile_no=mobile_no,department=department).save()
        messages.info(request,"SUSTAINER Registration successful")
        return redirect('/sus_reg/')
    else:
        return render(request,"sus/sus_login.html")
    
def sus_validate_login(request):
    if request.method=='POST':
        
        email = request.POST['email']
        password = request.POST['password']
        try:        
            data = registration.objects.get(email=email, password=password, department="SUSTAINER")
            if data.accept:   
                data.login = True
                data.logout = False
                data.save()

                # Store all three safely
                request.session['user_id'] = data.id
                request.session['email'] = data.email
                request.session['department'] = data.department

                messages.info(request, "SUSTAINER Login Successful")     
                return redirect("/sus_home/")
            else:
                messages.info(request, "Wrong Credentials")
                return redirect("/sus_login/")
        except:
            messages.info(request, "Wrong Credentials")
            return redirect("/sus_login/")
    return render(request, "sus/sus_login.html")


def sus_logout(request):
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

    messages.info (request,"SUSTAINER Logout Successfull")
    return redirect("/")

from django.shortcuts import get_object_or_404, render, redirect
from django.core.mail import send_mail
from django.contrib import messages


from .crypto_utils import encrypt_data, decrypt_data, generate_token, verify_token


def sus_req(request):
    if request.session.get('department') != "SUSTAINER":
        messages.error(request, "Unauthorized Access")
        return redirect("/sus_login/")

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
        if not item.e_recovered_metal:
            item.e_recovered_metal = encrypt_data(str(item.recovered_metal or ""))
        if not item.e_loss:
            item.e_loss = encrypt_data(str(item.loss or ""))
        if not item.e_recovery:
            item.e_recovery = encrypt_data(str(item.recovery or ""))

        item.save()

    return render(request, "sus/sus_req.html", {"data": data})

def getkey_sus(request, project_id):
    if request.session.get('department') != "SUSTAINER":
        messages.error(request, "Unauthorized Access")
        return redirect("/sus_login/")

    data = get_object_or_404(phytomine, project_id=project_id)
    reg_obj = get_object_or_404(registration, login=True, logout=False, department="SUSTAINER")

    token = generate_token(data.pk)

    data.sus_decrypt_key = token
    data.sus_get_key = True
    data.save()

    send_mail(
        "SUSTAINER: Secure Decryption Token",
        f"Project ID: {data.project_id}\n\nYour Secure Token:\n{token}",
        settings.EMAIL_HOST_USER,
        [reg_obj.email],
        fail_silently=False,
    )

    messages.success(request, "Secure decryption key sent successfully")
    return redirect("/sus_req/")

def decrypt_sus(request, project_id):
    if request.session.get('department') != "SUSTAINER":
        messages.error(request, "Unauthorized Access")
        return redirect("/sus_login/")

    d = get_object_or_404(phytomine, project_id=project_id)

    if request.method == "POST":
        token = request.POST.get("decryption_key", "").strip()

        try:
            if verify_token(token, d.pk):
                d.sus_decrypt = True
                # Digitally sign by storing user name
                user_id = request.session.get('user_id')
                if user_id:
                    try:
                        u = registration.objects.get(id=user_id)
                        d.sus_signed_by = u.name
                    except registration.DoesNotExist:
                        pass
                d.save()
                messages.success(request, f"{project_id}: Decryption Verified ✅")
            else:
                messages.error(request, f"{project_id}: Invalid or Expired Token ❌")

        except Exception as e:
            messages.error(request, f"Error: {str(e)}")

    return redirect("/sus_req/")

def sus_ana(request):
    if request.session.get('department') != "SUSTAINER":
        messages.error(request, "Unauthorized Access")
        return redirect("/sus_login/")
 
    data = phytomine.objects.all() 
    return render(request, "sus/sus_ana.html", {"data": data})

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans



def sus_ana_process(request, project_id):
    if request.session.get('department') != "SUSTAINER":
        messages.error(request, "Unauthorized Access")
        return redirect("/sus_login/")


    data = phytomine.objects.get(project_id=project_id)


    dataset_path = os.path.join(settings.BASE_DIR, 'dataset', 'sus.csv')
    df = pd.read_csv(dataset_path)

    feature_cols = [
        "INITIAL FERN BIOMASS (g)",
        "FINAL FERN BIOMASS (g)",
        "GROWTH DURATION (days)",
        "SOIL REE CONCENTRATION (mg/kg)",
        "PLANT REE CONCENTRATION (mg/kg)",
        "HARVESTED BIOMASS (g)",
        "EXTRACTION EFFICIENCY (%)",
        "INITIAL SOIL REE (mg/kg)",
        "FINAL SOIL REE (mg/kg)",
        "BIOMASS INCREASE (g)",
        "GROWTH RATE (g/day)",
        "GROWTH EFFICIENCY (%)",
        "TOTAL METAL (mg)",
        "UPTAKE (%)",
        "BAF",
        "RECOVERED METAL (mg)",
        "EXTRACTION LOSS (mg)",
        "RECOVERY PERCENTAGE (%)"
    ]

    target_cols = ["Reduction (%)", "Safety Index"]

    X = df[feature_cols].values
    y = df[target_cols]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # ------------------------------
    # K-Means Clustering
    # ------------------------------
    kmeans = KMeans(n_clusters=5, random_state=42)
    clusters = kmeans.fit_predict(X_scaled)
    df["cluster"] = clusters

    # ------------------------------
    # Prepare input
    # ------------------------------
    input_data = np.array([[  
        data.initial_fern_biomass,
        data.final_fern_biomass,
        data.growth_duration,
        data.soil_ree_conc,
        data.plant_ree_conc,
        data.harvested_biomass,
        data.extraction_eff,
        data.initial_soil_ree,
        data.final_soil_ree,
        data.biomass_increase,
        data.growth_rate,
        data.growth_eff,
        data.total_metal,
        data.uptake,
        data.baf,
        data.recovered_metal,
        data.loss,
        data.recovery,
    ]])

    input_scaled = scaler.transform(input_data)
    cluster_id = kmeans.predict(input_scaled)[0]

    # ------------------------------
    # Fetch REAL values from dataset
    # ------------------------------
    cluster_data = df[df["cluster"] == cluster_id]

    reduction = cluster_data["Reduction (%)"].mean()
    safety_index = cluster_data["Safety Index"].mean()

    # ------------------------------
    # Save results
    # ------------------------------
    data.reduction = round(float(reduction), 2)
    data.safety_index = round(float(safety_index), 2)

    data.env_status = "Safe" if data.safety_index <= 3 else "Unsafe"

    data.sus_scan = True
    data.status = "SUSTAINER Analysis Completed"
    data.save()

    messages.info(request, "SUSTAINER Analysis Completed")
    return redirect("/sus_ana/")



def sus_rep(request):
    if request.session.get('department') != "SUSTAINER":
        messages.error(request, "Unauthorized Access")
        return redirect("/sus_login/")

    data = phytomine.objects.all()
    return render(request, "sus/sus_rep.html", {"data": data})