from admins.models import registration, phytomine

def admin_notifications(request):
    """
    Context processor to inject notification counts into admin templates.
    """
    if request.session.get('role') == 'admin':
        # Notifications for new registrations waiting for approval
        pending_cul = registration.objects.filter(department="CULTIVATOR", accept=False, reject=False).count()
        pending_acc = registration.objects.filter(department="ACCUMULATOR", accept=False, reject=False).count()
        pending_ext = registration.objects.filter(department="EXTRACTOR", accept=False, reject=False).count()
        pending_sus = registration.objects.filter(department="SUSTAINER", accept=False, reject=False).count()

        pending_users = pending_cul + pending_acc + pending_ext + pending_sus
        
        # Notifications for fully completed modules that have generated reports but not yet viewed by Admin
        completed_modules = phytomine.objects.filter(sus_scan=True, admins_f_rep_view=False).count()
        
        total_notifications = completed_modules
        
        return {
            'pending_users_count': pending_users,
            'completed_modules_count': completed_modules,
            'total_notifications': total_notifications,
            'pending_cul': pending_cul,
            'pending_acc': pending_acc,
            'pending_ext': pending_ext,
            'pending_sus': pending_sus,
        }
    return {}
