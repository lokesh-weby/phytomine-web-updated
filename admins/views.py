from django.shortcuts import render, redirect, HttpResponse
from django.http import FileResponse, JsonResponse
import requests
from .models import *
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import os
import json
from google import genai

# Create your views here.

# Define the model architecture for soil classification
def get_soil_model():
    # Use weights=None instead of deprecated pretrained=False
    try:
        model = models.resnet18(weights=None)
    except TypeError:
        # Compatibility with older torchvision
        model = models.resnet18(pretrained=False)
    
    num_features = model.fc.in_features
    model.fc = nn.Sequential(
        nn.Linear(num_features, 512),
        nn.ReLU(inplace=True),
        nn.Dropout(0.5),
        nn.Linear(512, 256),
        nn.ReLU(inplace=True),
        nn.Dropout(0.3),
        nn.Linear(256, 4)
    )
    model_path = os.path.join(settings.BASE_DIR, "models", "soil_classifier_resnet18.pth")
    if os.path.exists(model_path):
        model.load_state_dict(torch.load(model_path, map_location='cpu'))
    model.eval()
    return model

def predict_soil(image_path):
    model = get_soil_model()
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(
            [0.485, 0.456, 0.406],
            [0.229, 0.224, 0.225]
        )
    ])
    classes = ['Black Soil', 'Clay soil', 'Alluvial soil', 'Red soil']
    img = Image.open(image_path).convert("RGB")
    img = transform(img).unsqueeze(0)
    with torch.no_grad():
        output = model(img)
        probs = torch.softmax(output, dim=1)
        pred = torch.argmax(probs, dim=1)
        confidence = probs[0][pred]
    return classes[pred.item()], float(confidence) * 100

def home(request):
    return render(request,"home/home.html")

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
        'Hello {0},\n\nWe are glad to inform you that your **{1} module profile has been approved successfully**.\n\nHere are your login details:\n• Username: "{2}"\n• Password: "{3}"\n\nPlease use these credentials to access the Portal.\n\nThank you,\nAdmin Team'.format(data.name, data.department, data.email, data.password),
        settings.EMAIL_HOST_USER,
        [data.email],
        fail_silently=False,
    )

    data.accept=True
    data.reject=False
    data.save()
    messages.info(request,f"{data.rh_id} Approval Successful")
    return redirect("/admins_home/")


def reject(request,id):
    if request.session.get('role') != "admin":
        return redirect("/admins_login/")
    data = registration.objects.get(id=id)
    data.accept=False
    data.reject=True
    data.save()
    send_mail('Rejection Mail', f'Hello {data.name}, your registration has been rejected.', settings.EMAIL_HOST_USER, [data.email], fail_silently=False)
    messages.info(request, "Rejection Mail Sent")
    return redirect("/admins_home/")

def admins_home(request):
    if request.session.get('role') != "admin":
        return redirect("/admins_login/")
    return render(request, 'admins/admins_home.html')

def admins_logout(request):
    request.session.flush()
    messages.info(request,"Admin Logout Successful")
    return redirect("/")

def cul_approve(request):
    if request.session.get('role') != "admin": return redirect("/admins_login/")
    data=registration.objects.filter(department="CULTIVATOR")
    return render(request,"admins/cul_approve.html",{'data':data})

def acc_approve(request):
    if request.session.get('role') != "admin": return redirect("/admins_login/")
    data=registration.objects.filter(department="ACCUMULATOR")
    return render(request,"admins/acc_approve.html",{'data':data})

def ext_approve(request):
    if request.session.get('role') != "admin": return redirect("/admins_login/")
    data=registration.objects.filter(department="EXTRACTOR")
    return render(request,"admins/ext_approve.html",{'data':data})

def sus_approve(request):
    if request.session.get('role') != "admin": return redirect("/admins_login/")
    data=registration.objects.filter(department="SUSTAINER")
    return render(request,"admins/sus_approve.html",{'data':data})

def admins_req(request):
    if request.session.get('role') != "admin": return redirect("/admins_login/")
    if request.method == "POST":
        p = request.POST
        last = phytomine.objects.all().order_by('id').last()
        try:
            project_id = max(int(last.project_id), 13200) + 1 if last and str(last.project_id).isdigit() else 13201
        except: project_id = 13201
        phytomine(initial_fern_biomass=p.get("initial_fern_biomass"), final_fern_biomass=p.get("final_fern_biomass"),
                 growth_duration=p.get("growth_duration"), soil_ree_conc=p.get("soil_ree_conc"),
                 plant_ree_conc=p.get("plant_ree_conc"), harvested_biomass=p.get("harvested_biomass"),
                 extraction_eff=p.get("extraction_eff"), initial_soil_ree=p.get("initial_soil_ree"),
                 final_soil_ree=p.get("final_soil_ree"), project_id=project_id, 
                 location=p.get("location"), soil_type=p.get("soil_type")).save()
        messages.info(request,"Requirements Submitted Successfully")
        return redirect('/admins_req/')
    return render(request, "admins/admins_req.html")

from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

@csrf_exempt
def predict_soil_type_ajax(request):
    if request.method == "POST" and request.FILES.get('soil_image'):
        image_file = request.FILES['soil_image']
        temp_path = default_storage.save('tmp/soil_predict_temp.jpg', ContentFile(image_file.read()))
        full_temp_path = os.path.join(settings.MEDIA_ROOT, temp_path)
        try:
            soil_type, confidence = predict_soil(full_temp_path)
            if os.path.exists(full_temp_path): os.remove(full_temp_path)
            return JsonResponse({"status": "success", "soil_type": soil_type, "confidence": round(confidence, 2)})
        except Exception as e:
            if os.path.exists(full_temp_path): os.remove(full_temp_path)
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)
    
def admins_status(request):
    if request.session.get('role') != "admin": return redirect("/admins_login/")
    data=phytomine.objects.all()
    return render (request,"admins/admins_status.html",{'data':data})

def rep_cul(request):
    if request.session.get('role') != "admin": return redirect("/admins_login/")
    data=phytomine.objects.all(); return render (request,"admins/rep_cul.html",{'data':data})

def rep_acc(request):
    if request.session.get('role') != "admin": return redirect("/admins_login/")
    data=phytomine.objects.all(); return render (request,"admins/rep_acc.html",{'data':data})

def rep_ext(request):
    if request.session.get('role') != "admin": return redirect("/admins_login/")
    data=phytomine.objects.all(); return render (request,"admins/rep_ext.html",{'data':data})

def rep_sus(request):
    if request.session.get('role') != "admin": return redirect("/admins_login/")
    data=phytomine.objects.all(); return render (request,"admins/rep_sus.html",{'data':data})

def download_report(request, project_id):
    """Serve the generated PDF with technical debug transparency."""
    if request.session.get('role') != "admin":
        return redirect("/admins_login/")
    
    try:
        # Match using project_id (CharField)
        record = phytomine.objects.get(project_id=str(project_id))
        
        if not record.admins_f_report:
            messages.error(request, f"Dossier #{project_id} has not been generated yet.")
            return redirect("/admins_status/")
            
        file_handle = record.admins_f_report.open('rb')
        response = FileResponse(file_handle, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="PHYTOMINE_REPORT_{project_id}.pdf"'
        return response

    except phytomine.DoesNotExist:
        messages.error(request, f"Failure: Record #{project_id} not located.")
        return redirect("/admins_status/")
    except FileNotFoundError:
        messages.error(request, "Physical report file missing from server storage.")
        return redirect("/admins_status/")
    except Exception as e:
        messages.error(request, f"Technical Failure: {str(e)}")
        return redirect("/admins_status/")

from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def get_ai_suggestions(user):
    try:
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not api_key: return "AI unavailable"
        client = genai.Client(api_key=api_key)
        prompt = f"Expert analysis for Project {user.project_id} at {user.location}. Soil {user.soil_type}. Suggest alternative plants and REE status."
        response = client.models.generate_content(model="gemini-3-flash-preview", contents=prompt)
        return response.text.strip()
    except: return "AI failed"

def phytomine_generate_pdf(request, project_id):
    if request.session.get('role') != "admin":
        messages.error(request, "Unauthorized Access")
        return redirect("/admins_login/")

    try:
        user = phytomine.objects.get(project_id=project_id)
        
        sections = {
            "ADMIN DATA": [
                ["INITIAL BIOMASS (g)", str(user.initial_fern_biomass)],
                ["FINAL BIOMASS (g)", str(user.final_fern_biomass)],
                ["GROWTH DURATION (days)", str(user.growth_duration)],
                ["SOIL TYPE", str(user.soil_type)],
                ["INITIAL SOIL REE (mg/kg)", str(user.initial_soil_ree)],
                ["FINAL SOIL REE (mg/kg)", str(user.final_soil_ree)],
            ],
            "CULTIVATOR ANALYTICS": [
                ["BIOMASS INCREASE (g)", str(user.biomass_increase)],
                ["GROWTH RATE (g/day)", str(user.growth_rate)],
                ["GROWTH EFFICIENCY (%)", str(user.growth_eff)],
            ],
            "ACCUMULATOR DATA": [
                ["TOTAL METAL UPTAKE (mg)", str(user.total_metal)],
                ["UPTAKE PERCENTAGE (%)", str(user.uptake)],
                ["BIOACCUMULATION FACTOR", str(user.baf)],
            ],
            "EXTRACTOR METRICS": [
                ["RECOVERED METAL (mg)", str(user.recovered_metal)],
                ["EXTRACTION LOSS (mg)", str(user.loss)],
                ["RECOVERY EFFICIENCY (%)", str(user.recovery)],
            ],
            "SUSTAINER STATUS": [
                ["SOIL REDUCTION (%)", str(user.reduction)],
                ["SAFETY INDEX", str(user.safety_index)],
                ["ENVIRONMENTAL STATUS", str(user.env_status)],
            ],
        }

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle('TitleStyle', fontSize=20, leading=24, alignment=1, textColor=colors.HexColor("#eb1616"), spaceAfter=30)
        story.append(Paragraph(f"PHYTOMINE DOSSIER: #{user.project_id}", title_style))
        story.append(Paragraph(f"<b>Location:</b> {user.location}", styles["Normal"]))
        story.append(Spacer(1, 25))

        header_color = colors.HexColor("#eb1616")
        
        for section_name, data in sections.items():
            story.append(Paragraph(f"<b>{section_name}</b>", styles["Heading2"]))
            story.append(Spacer(1, 10))
            
            table_data = [["Metric", "Value"]] + data
            table = Table(table_data, colWidths=[220, 240])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), header_color),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('TOPPADDING', (0, 0), (-1, -1), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
            ]))
            story.append(table)
            story.append(Spacer(1, 20))

        doc.build(story)
        pdf_data = buffer.getvalue()
        buffer.close()

        # If data is somehow empty, raise error
        if not pdf_data:
            raise ValueError("Generated PDF bytes are empty.")

        # Save to DB - use timestamp to force new file and prevent caching
        import time
        timestamp = int(time.time())
        filename = f"REPORT_{user.project_id}_{timestamp}.pdf"
        
        user.admins_f_report.save(filename, ContentFile(pdf_data))
        user.admins_f_rep_view = True
        user.save()

        messages.info(request, f"Dossier for project {user.project_id} generated successfully.")
        return redirect(f"/phytomine_dashboard/{project_id}/")

    except phytomine.DoesNotExist:
        messages.error(request, f"Failure: Record for ID {project_id} not located.")
        return redirect("/admins_status/")
    except Exception as e:
        messages.error(request, f"Technical Failure: {str(e)}")
        return redirect("/admins_status/")

def get_ai_insights(user):
    """Generate exactly 4 one-line expert points for the dashboard in JSON format."""
    try:
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not api_key: return json.dumps({"error": "No API Key"})
        client = genai.Client(api_key=api_key)
        prompt = f"""Analyze Project {user.project_id} (Soil: {user.soil_type}, Eff: {user.extraction_eff}%).
Return exactly 4 points in JSON format:
{{
  "OTHER CROPS": "one short line",
  "PROGRESSION": "one short line",
  "DURATION": "one short line",
  "SUGGESTED PLANTS": "one short line"
}}"""
        response = client.models.generate_content(model="gemini-3-flash-preview", contents=prompt)
        text = response.text.strip()
        # Extract JSON if markdown wrapped
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        return text
    except Exception as e:
        return json.dumps({"error": str(e)})

def phytomine_dashboard(request, project_id):
    if request.session.get('role') != "admin": return redirect("/admins_login/")
    try:
        data = phytomine.objects.get(project_id=project_id)
        
        # Check flag in DB first
        if data.is_insights_generated:
            try:
                insight_obj = phytomine_insights.objects.get(project=data)
                insights = json.loads(insight_obj.insights_text)
            except (phytomine_insights.DoesNotExist, json.JSONDecodeError):
                # Fallback if flag is true but record is missing or corrupted
                raw_insights = get_ai_insights(data)
                phytomine_insights.objects.update_or_create(project=data, defaults={'insights_text': raw_insights})
                try: insights = json.loads(raw_insights)
                except: insights = {"AI Analysis": raw_insights}
        else:
            # Generate for the first time
            raw_insights = get_ai_insights(data)
            phytomine_insights.objects.update_or_create(project=data, defaults={'insights_text': raw_insights})
            data.is_insights_generated = True
            data.save()
            try: insights = json.loads(raw_insights)
            except: insights = {"AI Analysis": raw_insights}
        
        return render(request, "admins/phytomine_dashboard.html", {'data': data, 'insights': insights})
    except: return redirect("/admins_status/")

def get_location_proxy(request):
    lat, lon = request.GET.get('lat'), request.GET.get('lon')
    if not lat or not lon: return JsonResponse({"error": "Req coord"}, status=400)
    url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
    try:
        r = requests.get(url, headers={'User-Agent': 'PhytomineApp/1.0'}, timeout=10)
        return JsonResponse(r.json())
    except: return JsonResponse({"error": "Fetch fail"}, status=500)