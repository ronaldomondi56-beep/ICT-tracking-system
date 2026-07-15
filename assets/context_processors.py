from .models import MaintenanceTicket


def sidebar_notifications(request):
    if not request.user.is_authenticated:
        return {}

    try:
        is_admin = request.user.is_superuser or request.user.is_staff
        department = request.user.profile.department if hasattr(request.user, 'profile') else None

        if is_admin:
            # Admin sees all open tickets and all pending approvals
            open_tickets_count = MaintenanceTicket.objects.filter(
                status='Open'
            ).count()

            pending_approvals_count = MaintenanceTicket.objects.filter(
                status='Replacement Requested'
            ).count()

            network_issues_count = MaintenanceTicket.objects.filter(
                status='Open',
                ticket_type='Network'
            ).count()

        else:
            # Regular user only sees their own tickets
            user_tickets = MaintenanceTicket.objects.filter(
                reported_by=request.user
            )

            open_tickets_count = user_tickets.filter(status='Open').count()
            pending_approvals_count = 0  # Regular users don't see finance approvals
            network_issues_count = user_tickets.filter(
                status='Open',
                ticket_type='Network'
            ).count()

    except Exception:
        open_tickets_count = 0
        pending_approvals_count = 0
        network_issues_count = 0

    return {
        'open_tickets_count': open_tickets_count,
        'pending_approvals_count': pending_approvals_count,
        'network_issues_count': network_issues_count,
    }