import os
from django.conf import settings
from django.shortcuts import redirect

class DevAutoLoginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Read the environment setting
        environment = getattr(settings, 'ENVIRONMENT', 'development').lower().strip()

        # If it's not production (meaning it is development)
        if environment != 'production':
            path = request.path
            
            # Auto-populate session credentials and redirect from login screens to home
            if path.startswith('/cul'):
                request.session['department'] = "CULTIVATOR"
                request.session['user_id'] = 9991
                request.session['name'] = "Lokesh"
                request.session['email'] = "lokesh0212004@gmail.com"
                if path in ('/cul_login/', '/cul_login'):
                    return redirect('/cul_home/')
                    
            elif path.startswith('/acc'):
                request.session['department'] = "ACCUMULATOR"
                request.session['user_id'] = 9992
                request.session['name'] = "Kishore"
                request.session['email'] = "lokesh0212004@gmail.com"
                if path in ('/acc_login/', '/acc_login'):
                    return redirect('/acc_home/')
                    
            elif path.startswith('/ext'):
                request.session['department'] = "EXTRACTOR"
                request.session['user_id'] = 9993
                request.session['name'] = "James"
                request.session['email'] = "lokesh0212004@gmail.com"
                if path in ('/ext_login/', '/ext_login'):
                    return redirect('/ext_home/')
                    
            elif path.startswith('/sus'):
                request.session['department'] = "SUSTAINER"
                request.session['user_id'] = 9994
                request.session['name'] = "Jerry"
                request.session['email'] = "lokesh0212004@gmail.com"
                if path in ('/sus_login/', '/sus_login'):
                    return redirect('/sus_home/')

        response = self.get_response(request)
        return response

