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
import qrcode
import uuid

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
            request.session['name'] = "Admin"
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


def remove_user(request, id):
    if request.session.get('role') != "admin":
        return redirect("/admins_login/")
    data = registration.objects.get(id=id)
    dept = data.department
    data.delete()
    messages.info(request, f"{data.name} has been removed successfully.")
    
    if dept == "CULTIVATOR": return redirect("/cul_approve/")
    elif dept == "ACCUMULATOR": return redirect("/acc_approve/")
    elif dept == "EXTRACTOR": return redirect("/ext_approve/")
    elif dept == "SUSTAINER": return redirect("/sus_approve/")
    return redirect("/admins_home/") 

def update_user(request, id):

    if request.session.get('role') != "admin":
        return redirect("/admins_login/")

    data = registration.objects.get(id=id)

    if request.method == "POST":

        data.name = request.POST.get('name')
        data.department = request.POST.get('department')
        data.email = request.POST.get('email')
        data.mobile_no = request.POST.get('mobile_no')

        data.save()

        messages.success(
            request,
            f"{data.name} updated successfully."
        )

        # REDIRECT AFTER UPDATE
        if data.department == "CULTIVATOR":
            return redirect("/cul_approve/")

        elif data.department == "ACCUMULATOR":
            return redirect("/acc_approve/")

        elif data.department == "EXTRACTOR":
            return redirect("/ext_approve/")

        elif data.department == "SUSTAINER":
            return redirect("/sus_approve/")

        return redirect("/admins_home/")

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
        
        # Save the new entry (Phase 1 fields only)
        new_project = phytomine(
            initial_fern_biomass=p.get("initial_fern_biomass"), 
            growth_duration=p.get("growth_duration"), 
            soil_ree_conc=p.get("soil_ree_conc"),
            initial_soil_ree=p.get("initial_soil_ree"),
            project_id=project_id, 
            location=p.get("location"), 
            soil_type=p.get("soil_type")
        )
        new_project.save()

        # Generate QR Code (encoding the Project ID)
        qr = qrcode.make(str(project_id))
        qr_io = BytesIO()
        qr.save(qr_io, format='PNG')
        qr_file = ContentFile(qr_io.getvalue(), name=f"qr_{new_project.tracking_id}.png")
        new_project.qr_code.save(f"qr_{new_project.tracking_id}.png", qr_file, save=True)

        # Store QR URL in session to display it on the next page
        request.session['latest_qr'] = new_project.qr_code.url
        request.session['latest_tracking_id'] = str(new_project.tracking_id)

        messages.info(request,"Phase 1 Data Saved Successfully. QR Code generated!")
        return redirect('/admins_req/')
    
    context = {}
    if 'latest_qr' in request.session:
        context['latest_qr'] = request.session.pop('latest_qr')
        context['latest_tracking_id'] = request.session.pop('latest_tracking_id')
    
    context['all_projects'] = phytomine.objects.all().order_by('-id')

    return render(request, "admins/admins_req.html", context)

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
    try:
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            return None

        client = genai.Client(api_key=api_key)

        prompt = f"""Analyze Project {user.project_id} (Soil: {user.soil_type}, Eff: {user.extraction_eff}%).
Return exactly 4 points in JSON format:
{{
  "OTHER CROPS": "one short line",
  "PROGRESSION": "one short line",
  "DURATION": "one short line",
  "SUGGESTED PLANTS": "one short line"
}}"""

        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt
        )

        text = response.text.strip()

        # Clean markdown
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()

        # Validate JSON before returning
        json.loads(text)

        return text  # ✅ Only valid JSON returned

    except Exception:
        return None  # ❌ No invalid data

def phytomine_dashboard(request, project_id):
    if request.session.get('role') != "admin":
        return redirect("/admins_login/")

    try:
        data = phytomine.objects.get(project_id=project_id)

        insights = None

        # ✅ Try DB first
        if data.is_insights_generated:
            try:
                insight_obj = phytomine_insights.objects.get(project=data)
                insights = json.loads(insight_obj.insights_text)
            except:
                insights = None  # force retry

        # If no valid insights → call AI
        if not insights:
            raw_insights = get_ai_insights(data)

            if raw_insights:
                # Save ONLY if success
                phytomine_insights.objects.update_or_create(
                    project=data,
                    defaults={'insights_text': raw_insights}
                )
                data.is_insights_generated = True
                data.save()

                insights = json.loads(raw_insights)

            else:
                #  Do NOT save anything
                insights = {
                    "AI STATUS": "AI service is not available"
                }

        return render(request, "admins/phytomine_dashboard.html", {
            'data': data,
            'insights': insights
        })

    except:
        return redirect("/admins_status/")
def get_location_proxy(request):
    lat, lon = request.GET.get('lat'), request.GET.get('lon')
    if not lat or not lon: return JsonResponse({"error": "Req coord"}, status=400)
    url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
    try:
        r = requests.get(url, headers={'User-Agent': 'PhytomineApp/1.0'}, timeout=10)
        return JsonResponse(r.json())
    except: return JsonResponse({"error": "Fetch fail"}, status=500)

def chatbot(request):
    """Static Chatbot: Direct DB answers only, no AI."""
    if request.session.get('role') != "admin":
        return JsonResponse({"error": "Unauthorized"}, status=403)

    user_input = request.GET.get("message", "").strip().lower()
    if not user_input:
        return JsonResponse({"error": "No message provided"}, status=400)

    import re

    # 1. Recent Logins Handler
    if "recent logins" in user_input:
        data = registration.objects.filter(login=True).order_by("-id")[:10]
        if not data: return JsonResponse({"message": "No recent logins found."})
        table = "| Name | Email | Dept | Status |\n| :--- | :--- | :--- | :--- |\n"
        for r in data:
            table += f"| {r.name} | {r.email} | {r.department} | Active |\n"
        return JsonResponse({"message": f"### Recent Logins\n{table}"})

    # 2. Get Report Handler (Dynamic Selection)
    if user_input == "report":
        projects = phytomine.objects.all().order_by('-id')
        ids = [p.project_id for p in projects]
        return JsonResponse({
            "message": "Please select the **Project ID** to generate the PDF dossier:",
            "options": ids,
            "type": "report"
        })

    # 3. Specific Report ID Handler (e.g., "report 13205")
    if "report" in user_input:
        match = re.search(r'\d+', user_input)
        if match:
            p_id = match.group()
            try:
                proj = phytomine.objects.get(project_id=p_id)
                link = f"/download_report/{p_id}/"
                return JsonResponse({
                    "message": f"### Dossier Link for #{p_id}\n\n[📥 Download PDF Report]({link})"
                })
            except phytomine.DoesNotExist:
                return JsonResponse({"message": f"❌ Project ID #{p_id} not found."})

    # 4. Project Progress Handler (Dynamic Selection)
    if user_input == "progress":
        projects = phytomine.objects.all().order_by('-id')
        ids = [p.project_id for p in projects]
        return JsonResponse({
            "message": "Select a **Project ID** to view real-time lifecycle status:",
            "options": ids,
            "type": "progress"
        })

    # 5. Specific Progress ID Handler (e.g., "progress 13205")
    if "progress" in user_input:
        match = re.search(r'\d+', user_input)
        if match:
            p_id = match.group()
            try:
                proj = phytomine.objects.get(project_id=p_id)
                status_table = f"""
| Module | Status |
| :--- | :--- |
| **Cultivator** | {'✅ Done' if proj.cul_scan else '⏳ Pending'} |
| **Accumulator** | {'✅ Done' if proj.acc_scan else '⏳ Pending'} |
| **Extractor** | {'✅ Done' if proj.ext_scan else '⏳ Pending'} |
| **Sustainer** | {'✅ Done' if proj.sus_scan else '⏳ Pending'} |
"""
                return JsonResponse({"message": f"### Progress for Project {p_id}\n{status_table}"})
            except phytomine.DoesNotExist:
                return JsonResponse({"message": f"❌ No progress data for #{p_id}."})

    # 6. User Directory Handler
    if "users" in user_input or "personnel" in user_input or "user" == user_input:
        data = registration.objects.filter(accept=True)
        if not data: return JsonResponse({"message": "No approved users found."})
        table = "| Name | Department | Email |\n| :--- | :--- | :--- |\n"
        for r in data:
            table += f"| {r.name} | {r.department} | {r.email} |\n"
        return JsonResponse({"message": f"### Active Personnel Directory\n{table}"})

    # 7. Rejection History Handler
    if "rejection history" in user_input:
        data = registration.objects.filter(reject=True)
        if not data: return JsonResponse({"message": "No rejections found."})
        table = "| Name | Department | Email |\n| :--- | :--- | :--- |\n"
        for r in data:
            table += f"| {r.name} | {r.department} | {r.email} |\n"
        return JsonResponse({"message": f"### Rejection History\n{table}"})

    # 8. Pending Approvals Alert Handler
    if "approvals" in user_input:
        pending = registration.objects.filter(accept=False, reject=False)
        if not pending: return JsonResponse({"message": "All caught up! No pending approvals."})
        
        summary = {}
        for r in pending:
            summary[r.department] = summary.get(r.department, 0) + 1
        
        msg = "### 🔔 Pending Approvals\n\n"
        for dept, count in summary.items():
            msg += f"- **{dept}**: {count} request(s)\n"
        msg += "\nGo to the respective 'Approve' sections to take action."
        return JsonResponse({"message": msg})

    # Default Help
    return JsonResponse({
        "message": "Unrecognized command. Try clicking one of the **Quick Action Tabs** above or type a command like `approvals`, `report [ID]`, or `progress [ID]`."
    })

def phase_two(request):
    if request.session.get('role') != "admin": return redirect("/admins_login/")
    
    # Get all projects for the dropdown
    projects = phytomine.objects.all().order_by('-id')
    
    selected_project = None
    if request.method == "POST":
        p = request.POST
        project_id = p.get("project_id")
        
        try:
            selected_project = phytomine.objects.get(project_id=project_id)
            
            # If they submitted the Phase 2 data fields
            if p.get("final_fern_biomass") or p.get("plant_ree_conc"):
                if p.get("final_fern_biomass"):
                    selected_project.final_fern_biomass = float(p.get("final_fern_biomass"))
                if p.get("harvested_biomass"):
                    selected_project.harvested_biomass = float(p.get("harvested_biomass"))
                if p.get("final_soil_ree"):
                    selected_project.final_soil_ree = float(p.get("final_soil_ree"))
                if p.get("plant_ree_conc"):
                    selected_project.plant_ree_conc = float(p.get("plant_ree_conc"))
                if p.get("extraction_eff"):
                    selected_project.extraction_eff = float(p.get("extraction_eff"))
                if p.get("recovery"):
                    selected_project.recovery = float(p.get("recovery"))
                if p.get("safety_index"):
                    selected_project.safety_index = float(p.get("safety_index"))
                    
                selected_project.save()
                messages.success(request, f"Phase 2 data for Project {project_id} updated successfully!")
                return redirect("/phase_two/")
                
        except phytomine.DoesNotExist:
            messages.error(request, "Invalid Project ID selected.")
            return redirect("/phase_two/")
            
    # If GET or if they just selected a project (via some AJAX or form refresh)
    project_id_param = request.GET.get('project_id')
    if project_id_param:
        try:
            selected_project = phytomine.objects.get(project_id=project_id_param)
        except phytomine.DoesNotExist:
            pass
            
    context = {"projects": projects, "data": selected_project}
    
    # Check if we just came from Phase 1 and have a new QR code to show
    if 'latest_qr' in request.session:
        context['latest_qr'] = request.session.pop('latest_qr')
        context['latest_tracking_id'] = request.session.pop('latest_tracking_id')

    return render(request, "admins/phase_two.html", context)

@csrf_exempt
def get_project_data_ajax(request, project_id):
    if request.session.get('role') != "admin":
        return JsonResponse({"status": "error", "message": "Unauthorized"}, status=403)
        
    try:
        project = phytomine.objects.get(project_id=project_id)
        data = {
            "status": "success",
            "location": project.location,
            "soil_type": project.soil_type,
            "initial_fern_biomass": project.initial_fern_biomass,
            "growth_duration": project.growth_duration,
            "initial_soil_ree": project.initial_soil_ree,
            "soil_ree_conc": project.soil_ree_conc
        }
        return JsonResponse(data)
    except phytomine.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Project not found"}, status=404)