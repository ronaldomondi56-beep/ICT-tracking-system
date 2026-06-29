from .models import MaintenanceTicket


def sidebar_notifications(request):
    """
    Makes notification badge counts available in every template
    (used by the sidebar in base.html).
    """
    if not request.user.is_authenticated:
        return {}

    open_tickets_count = MaintenanceTicket.objects.filter(status='Open').count()
    pending_approvals_count = MaintenanceTicket.objects.filter(
        status='Replacement Requested'
    ).count()

    return {
        'open_tickets_count': open_tickets_count,
        'pending_approvals_count': pending_approvals_count,
    }