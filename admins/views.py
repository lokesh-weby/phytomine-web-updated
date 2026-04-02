from django.shortcuts import render, redirect, HttpResponse
from django.http import FileResponse, JsonResponse
import requests
from .models import *
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings


# Create your views here.

def home(request):
    return render(request,"home/home.html")

# def admins_login(request):
#     if request.method == "POST":
#         try:
#             email=request.POST['email']
#             password=request.POST['password']
#             if email=="admin@gmail.com" and password=="admin":
#                 messages.info(request,"Admin Login Successful")
#                 return redirect("/admins_home/")
#             elif email !="admin@gmail.com" and password=="admin":
#                 messages.error(request, "Incorrect email!")
#                 return render(request,"admins/admins_login.html")
#             elif email =="admin@gmail.com" and password!="admin":
#                 messages.error(request, "Incorrect Password!")
#                 return render(request,"admins/admins_login.html")
#             elif email !="admin@gmail.com" and password!="admin":
#                 messages.error(request, "Incorrect email and Password!")
#                 return render(request,"admins/admins_login.html")
#             else:
#                 return render(request,"admins/admins_login.html")
#         except:
#             messages.error(request, "Incorrect Credentials!")
#     return render(request,"admins/admins_login.html")
def admins_login(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        role = request.POST['role']

        if email == "admin@gmail.com" and password == "admin" and role == "admin":
            request.session['role'] = role
            request.session['admin'] = email

            messages.info(request,"Admin Login Successful")
            return redirect("/admins_home/")

        elif email != "admin@gmail.com":
            messages.error(request, "Incorrect email!")

        elif password != "admin":
            messages.error(request, "Incorrect Password!")

        else:
            messages.error(request, "Incorrect Credentials!")

    return render(request,"admins/admins_login.html")

import random
def accept(request,id):
    if request.session.get('role') != "admin":
        messages.error(request, "Unauthorized Access")
        return redirect("/admins_login/")

    data=registration.objects.get(id=id)
    password=random.randint(10000,99999)
    rh_id=random.randint(1000,9999)
    
    data.password=password
    data.rh_id=f"ID:{rh_id}"
    data.save()

    send_mail(
        '{0}: Login Credentials'.format(data.department),

        'Hello {0},\n\n'
        'We are glad to inform you that your **{1} module profile has been approved successfully**.\n\n'
        'Here are your login details:\n'
        '• Username: "{2}"\n'
        '• Password: "{3}"\n\n'
        'Please use these credentials to access the **{4} Portal**. Make sure to keep this information confidential and do not share it with anyone.\n\n'
        'If you have any questions or face any issues while logging in, feel free to contact the support team.\n\n'
        'Thank you,\n'
        'Admin Team'
        .format(data.name, data.department, data.email, data.password, data.department.capitalize()),

        settings.EMAIL_HOST_USER,
        [data.email],
        fail_silently=False,
    )

    data.accept=True
    data.reject=False
    data.save()
    messages.info(request,f"{data.rh_id} : {data.department} Approval Successful")
    return redirect("/admins_home/")


def reject(request,id):
    if request.session.get('role') != "admin":
        messages.error(request, "Unauthorized Access")
        return redirect("/admins_login/")

    data = registration.objects.get(id=id)
    data.accept=False
    data.reject=True
    data.save()

    subject = 'Rejection Mail'
    plain_message = (
    f"Hello {data.name},\n\n"
    f"We regret to inform you that your registration has been **rejected** due to certain issues in the submitted details.\n"
    f"Please review your information and try submitting again at a later time.\n\n"
    f"If you need assistance or clarification, feel free to reach out to the support team.\n\n"
    f"Thank you for your understanding."
)
    send_mail(subject, plain_message, settings.EMAIL_HOST_USER, [data.email], fail_silently=False)

    # data.delete()
    messages.info(request, "Rejection Mail Sent")
    return redirect("/admins_home/")

# def admins_home(request):
#     return render (request, 'admins/admins_home.html')
def admins_home(request):
    if request.session.get('role') != "admin":
        messages.error(request,"Unauthorized Access")
        return redirect("/admins_login/")
        
    return render(request, 'admins/admins_home.html')


def admins_logout(request):
    request.session.flush()
    messages.info(request,"Admin Logout Successful")
    return redirect("/")

def cul_approve(request):
    if request.session.get('role') != "admin":
        messages.error(request,"Unauthorized Access")
        return redirect("/admins_login/")
    data=registration.objects.filter(department="CULTIVATOR")
    return render(request,"admins/cul_approve.html",{'data':data})

def acc_approve(request):
    if request.session.get('role') != "admin":
        messages.error(request,"Unauthorized Access")
        return redirect("/admins_login/")
    data=registration.objects.filter(department="ACCUMULATOR")
    return render(request,"admins/acc_approve.html",{'data':data})

def ext_approve(request):
    if request.session.get('role') != "admin":
        messages.error(request,"Unauthorized Access")
        return redirect("/admins_login/")
    data=registration.objects.filter(department="EXTRACTOR")
    return render(request,"admins/ext_approve.html",{'data':data})

def sus_approve(request):
    if request.session.get('role') != "admin":
        messages.error(request,"Unauthorized Access")
        return redirect("/admins_login/")
    data=registration.objects.filter(department="SUSTAINER")
    return render(request,"admins/sus_approve.html",{'data':data})

def admins_req(request):

    print(request.POST)
    if request.session.get('role') != "admin":
        messages.error(request,"Unauthorized Access")
        return redirect("/admins_login/")

    if request.method == "POST":
        initial_fern_biomass=request.POST.get("initial_fern_biomass")
        final_fern_biomass=request.POST.get("final_fern_biomass")
        growth_duration=request.POST.get("growth_duration") 
        soil_ree_conc=request.POST.get("soil_ree_conc")       
        plant_ree_conc=request.POST.get("plant_ree_conc")       
        harvested_biomass=request.POST.get("harvested_biomass")       
        extraction_eff=request.POST.get("extraction_eff")       
        initial_soil_ree=request.POST.get("initial_soil_ree")
        final_soil_ree=request.POST.get("final_soil_ree")
        location=request.POST.get("location")
        # Generate sequential project_id starting from 13201
        last_project = phytomine.objects.all().order_by('id').last()
        try:
            if last_project and last_project.project_id and str(last_project.project_id).isdigit():
                project_id = max(int(last_project.project_id), 13200) + 1
            else:
                project_id = 13201
        except (ValueError, TypeError):
            project_id = 13201
        phytomine(initial_fern_biomass=initial_fern_biomass, final_fern_biomass=final_fern_biomass, growth_duration=growth_duration,
                     soil_ree_conc=soil_ree_conc,plant_ree_conc=plant_ree_conc,harvested_biomass=harvested_biomass,extraction_eff=extraction_eff,
                     initial_soil_ree=initial_soil_ree,final_soil_ree=final_soil_ree,
                     project_id=project_id, location=location).save()
        messages.info(request,"Requirements Submitted Successfully")
        return redirect('/admins_req/')
    else:
        return render(request, "admins/admins_req.html")
    
def admins_status(request):
    if request.session.get('role') != "admin":
        messages.error(request,"Unauthorized Access")
        return redirect("/admins_login/")
    data=phytomine.objects.all()
    return render (request,"admins/admins_status.html",{'data':data})

def rep_cul(request):
    if request.session.get('role') != "admin":
        messages.error(request,"Unauthorized Access")
        return redirect("/admins_login/")
    data=phytomine.objects.all()
    return render (request,"admins/rep_cul.html",{'data':data})

def rep_acc(request):
    if request.session.get('role') != "admin":
        messages.error(request,"Unauthorized Access")
        return redirect("/admins_login/")
    data=phytomine.objects.all()
    return render (request,"admins/rep_acc.html",{'data':data})

def rep_ext(request):
    if request.session.get('role') != "admin":
        messages.error(request,"Unauthorized Access")
        return redirect("/admins_login/")
    data=phytomine.objects.all()
    return render (request,"admins/rep_ext.html",{'data':data})

def rep_sus(request):
    if request.session.get('role') != "admin":
        messages.error(request,"Unauthorized Access")
        return redirect("/admins_login/")
    data=phytomine.objects.all()
    return render (request,"admins/rep_sus.html",{'data':data})


def download_report(request, project_id):
    """Serve the generated PDF with correct headers so the browser downloads it as a .pdf file."""
    if request.session.get('role') != "admin":
        messages.error(request, "Unauthorized Access")
        return redirect("/admins_login/")
    try:
        record = phytomine.objects.get(project_id=project_id)
        if not record.admins_f_report:
            messages.error(request, "Report not found.")
            return redirect("/admins_status/")
        pdf_file = record.admins_f_report
        filename = f"PHYTOMINE_REPORT_{project_id}.pdf"
        return FileResponse(pdf_file.open('rb'), as_attachment=True, filename=filename)
    except phytomine.DoesNotExist:
        messages.error(request, "Project not found.")
        return redirect("/admins_status/")
    except Exception as e:
        messages.error(request, f"Download failed: {str(e)}")
        return redirect("/admins_status/")


from io import BytesIO
from django.core.files.base import ContentFile
from django.contrib import messages
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from google import genai
from google.genai import types
import os

def get_ai_suggestions(user):
    """Call Gemini API to generate expert suggestions based on project data."""
    try:
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            return "AI suggestion unavailable: GEMINI_API_KEY not configured in environment."
        genai_client = genai.Client(api_key=api_key)
        prompt = f"""You are an expert phytomining scientist and environmental consultant.
        say can I plant any other plant in this area ? and also recommend some other plants that can be planted in this area to extract REE from the soil. 
        after extracting the REE from the soil, the soil will be safe to plant any other plant. only answer for this question. keep response short and clean.

Project ID: {user.project_id}
Location: {user.location}

--- FIELD DATA ---
Initial Fern Biomass: {user.initial_fern_biomass} g
Final Fern Biomass: {user.final_fern_biomass} g
Growth Duration: {user.growth_duration} days
Soil REE Concentration: {user.soil_ree_conc} mg/kg
Plant REE Concentration: {user.plant_ree_conc} mg/kg
Harvested Biomass: {user.harvested_biomass} g
Extraction Efficiency: {user.extraction_eff}%
Initial Soil REE: {user.initial_soil_ree} mg/kg
Final Soil REE: {user.final_soil_ree} mg/kg

--- COMPUTED METRICS ---
Biomass Increase: {user.biomass_increase} g
Growth Rate: {user.growth_rate} g/day
Growth Efficiency: {user.growth_eff}%
Total Metal: {user.total_metal} mg
Uptake: {user.uptake}%
Bioaccumulation Factor (BAF): {user.baf}
Recovered Metal: {user.recovered_metal} mg
Extraction Loss: {user.loss} mg
Recovery Percentage: {user.recovery}%
Soil Metal Reduction: {user.reduction}%
Safety Index: {user.safety_index}
Environmental Status: {user.env_status}

Provide your expert recommendations:"""
        response = genai_client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt,
        )
        return response.text.strip()
    except Exception as e:
        return f"AI suggestion generation failed: {str(e)}"

def phytomine_generate_pdf(request, project_id):
    if request.session.get('role') != "admin":
        messages.error(request, "Unauthorized Access")
        return redirect("/admins_login/")

    user = phytomine.objects.get(project_id=project_id)
    title = "PHYTOMINE FINAL REPORT"

    client_info = [
        ["PROJECT ID", user.project_id],
        ["LOCATION", user.location],
    ]

    sections = {
        "ADMIN:": [
            ["INITIAL FERN BIOMASS (g)", str(user.initial_fern_biomass)],
            ["FINAL FERN BIOMASS (g)", str(user.final_fern_biomass)],
            ["GROWTH DURATION (days)", str(user.growth_duration)],
            ["SOIL REE CONCENTRATION (mg/kg)", str(user.soil_ree_conc)],
            ["PLANT REE CONCENTRATION (mg/kg)", str(user.plant_ree_conc)],
            ["HARVESTED BIOMASS (g)", str(user.harvested_biomass)],
            ["EXTRACTION EFFICIENCY (%)", str(user.extraction_eff)],
            ["INITIAL SOIL REE (mg/kg)", str(user.initial_soil_ree)],
            ["FINAL SOIL REE (mg/kg)", str(user.final_soil_ree)],
        ],
        "CULTIVATOR:": [
            ["BIOMASS INCREASE (g)", str(user.biomass_increase)],
            ["GROWTH RATE (g/day)", str(user.growth_rate)],
            ["GROWTH EFFICIENCY (%)", str(user.growth_eff)],
        ],
        "ACCUMULATOR:": [
            ["TOTAL METAL (mg)", str(user.total_metal)],
            ["UPTAKE (%)", str(user.uptake)],
            ["BAF", str(user.baf)],
        ],
        "EXTRACTOR:": [
            ["RECOVERED METAL (mg)", str(user.recovered_metal)],
            ["EXTRACTION LOSS (mg)", str(user.loss)],
            ["RECOVERY PERCENTAGE (%)", str(user.recovery)],
        ],
        "SUSTAINER:": [
            ["SOIL METAL REDUCTION (%)", str(user.reduction)],
            ["SAFETY INDEX", str(user.safety_index)],
            ["ENVIRONMENTAL STATUS", str(user.env_status)],
        ],
    }

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []

    styles = getSampleStyleSheet()

    # 🌿 Title style
    title_style = ParagraphStyle(
        name="CustomTitle",
        fontSize=18,
        leading=22,
        alignment=1,  # Center
        textColor=colors.HexColor("#eb1616"),  # Deep forest blue
        spaceAfter=20
    )
    title_para = Paragraph(title, title_style)
    story.append(title_para)

    # ✅ Color scheme
    header_bg = colors.HexColor("#eb1616")       # Medium Sea Green
    header_text = colors.white                  # White for text
    cell_bg = colors.HexColor("#F0FFF0")         # Honeydew
    section_heading_color = colors.HexColor("#eb1616")  # Dark Green

    # 🧾 Client info table
    client_info_table = Table(client_info, colWidths=[200, 250])
    client_info_table.setStyle(
        TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
            ("BACKGROUND", (0, 0), (-1, -1), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ])
    )
    story.append(client_info_table)
    story.append(Spacer(1, 20))

    # 📊 Each section table
    for section, data in sections.items():
        # Force new page if needed
        if section == "RELEASE:":
            story.append(PageBreak())

        section_title = Paragraph(
            f"<font color='{section_heading_color}'><b>{section}</b></font>",
            styles["Heading2"]
        )
        story.append(section_title)
        story.append(Spacer(1, 6))

        table_data = [["Title", "Value"]] + data
        table = Table(table_data, colWidths=[200, 250])
        table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), header_bg),
                ("TEXTCOLOR", (0, 0), (-1, 0), header_text),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), cell_bg),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ])
        )
        story.append(table)
        story.append(Spacer(1, 20))

    # --- AI Suggestions Section Removed ---


    # �🧱 Build the PDF
    doc.build(story)
    pdf_data = buffer.getvalue()
    buffer.close()

    user.admins_f_report.save(f"{title}_{user.project_id}.pdf", ContentFile(pdf_data))
    user.admins_f_rep_view = True
    user.save()

    messages.info(request, f"Report for {user.project_id} Generated Successfully")
    return redirect("/admins_status/")

def get_location_proxy(request):
    """Bypass CORS for Nominatim API by fetching on the server side."""
    lat = request.GET.get('lat')
    lon = request.GET.get('lon')
    
    if not lat or not lon:
        return JsonResponse({"error": "Latitude and longitude are required"}, status=400)

    url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
    headers = {
        'User-Agent': 'PhytomineApp/1.0 (Contact: admin@phytomine.com)'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        return JsonResponse(response.json())
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)