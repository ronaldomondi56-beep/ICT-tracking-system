from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.utils import timezone
from django.http import HttpResponseForbidden

from .models import Asset, MaintenanceTicket, UserProfile
from .forms import AssetForm, MaintenanceTicketForm, UserRegistrationForm


# ====================== HELPER FUNCTIONS ======================
def is_admin(user):
    return user.is_superuser or user.is_staff


def get_user_department(user):
    try:
        return user.profile.department
    except UserProfile.DoesNotExist:
        return None


# ====================== AUTHENTICATION ======================
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('dashboard')
    else:
        form = AuthenticationForm()

    return render(request, 'assets/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Account created successfully for {user.username}!")
            return redirect('login')
    else:
        form = UserRegistrationForm()

    return render(request, 'assets/register.html', {'form': form})


# ====================== DASHBOARD ======================
@login_required
def dashboard(request):
    user = request.user
    department = get_user_department(user)

    if is_admin(user):
        # Admin sees everything
        total_assets = Asset.objects.count()
        working = Asset.objects.filter(status='Working').count()
        outdated = Asset.objects.filter(status='Replacement Required').count()
        lost_damaged = Asset.objects.filter(status__in=['Lost', 'Damaged']).count()

        total_tickets = MaintenanceTicket.objects.count()
        open_tickets = MaintenanceTicket.objects.filter(status='Open').count()
        resolved = MaintenanceTicket.objects.filter(status='Resolved').count()

        recent_assets = Asset.objects.all().order_by('-id')[:5]
        recent_tickets = MaintenanceTicket.objects.all().order_by('-date_reported')[:5]
    else:
        # Regular user sees only their department's assets and their own tickets
        dept_assets = Asset.objects.filter(department=department) if department else Asset.objects.none()
        user_tickets = MaintenanceTicket.objects.filter(reported_by=user)

        total_assets = dept_assets.count()
        working = dept_assets.filter(status='Working').count()
        outdated = dept_assets.filter(status='Replacement Required').count()
        lost_damaged = dept_assets.filter(status__in=['Lost', 'Damaged']).count()

        total_tickets = user_tickets.count()
        open_tickets = user_tickets.filter(status='Open').count()
        resolved = user_tickets.filter(status='Resolved').count()

        recent_assets = dept_assets.order_by('-id')[:5]
        recent_tickets = user_tickets.order_by('-date_reported')[:5]

    context = {
        'total_assets': total_assets,
        'working': working,
        'outdated': outdated,
        'lost': lost_damaged,
        'total_tickets': total_tickets,
        'open_tickets': open_tickets,
        'resolved': resolved,
        'recent_assets': recent_assets,
        'recent_tickets': recent_tickets,
        'is_admin': is_admin(user),
    }

    return render(request, 'assets/dashboard.html', context)


# ====================== ASSET MANAGEMENT ======================
@login_required
def assetlist(request):
    user = request.user
    department = get_user_department(user)

    if is_admin(user):
        assets = Asset.objects.all().order_by('-id')
    else:
        assets = Asset.objects.filter(department=department).order_by('-id') if department else Asset.objects.none()

    search_query = request.GET.get('search', '').strip()
    if search_query:
        assets = assets.filter(
            Q(name__icontains=search_query) |
            Q(serial_number__icontains=search_query) |
            Q(department__icontains=search_query)
        )

    status_filter = request.GET.get('status', '')
    if status_filter:
        assets = assets.filter(status=status_filter)

    context = {
        'assets': assets,
        'search_query': search_query,
        'status_filter': status_filter,
        'is_admin': is_admin(user),
    }

    return render(request, 'assets/assetlist.html', context)


@login_required
@user_passes_test(is_admin)
def addasset(request):
    if request.method == "POST":
        form = AssetForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Asset added successfully!")
            return redirect('add_asset')  
    else:
        form = AssetForm()

    return render(request, 'assets/add_asset.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def asset_edit(request, pk):
    asset = get_object_or_404(Asset, pk=pk)

    if request.method == "POST":
        form = AssetForm(request.POST, instance=asset)
        if form.is_valid():
            form.save()
            messages.success(request, f'Asset "{asset.name}" updated successfully!')
            return redirect('asset_list')
    else:
        form = AssetForm(instance=asset)

    return render(request, 'assets/asset_edit.html', {'form': form, 'asset': asset})


@login_required
@user_passes_test(is_admin)
def asset_delete(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    if request.method == "POST":
        asset_name = asset.name
        asset.delete()
        messages.success(request, f'Asset "{asset_name}" deleted successfully!')
        return redirect('asset_list')

    return render(request, 'assets/asset_confirm_delete.html', {'asset': asset})


# ====================== TICKETING SYSTEM ======================
@login_required
def raise_ticket(request, asset_pk=None):
   
    if is_admin(request.user):
        messages.error(request, "Admins do not raise tickets.")
        return redirect('ticket_list')

    asset = get_object_or_404(Asset, pk=asset_pk) if asset_pk else None

    if request.method == "POST":
        form = MaintenanceTicketForm(request.POST, user=request.user)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.reported_by = request.user
            if asset:
                ticket.asset = asset
            # Auto-generate title from description
            description = form.cleaned_data.get('description', '')
            ticket.title = description[:80] if description else f'Issue with {ticket.asset.name}'
            try:
                profile = request.user.profile
                ticket.department = profile.department
                if not ticket.office_name:
                    ticket.office_name = profile.office_name
                if not ticket.door_number:
                    ticket.door_number = profile.door_number
                if not ticket.block:
                    ticket.block = profile.block
                if not ticket.floor:
                    ticket.floor = profile.floor
            except UserProfile.DoesNotExist:
                pass
            ticket.save()
            messages.success(request, f'Ticket #{ticket.id} raised successfully!')
            return redirect('ticket_list')
    else:
        initial = {}
        if asset:
            initial['asset'] = asset
        form = MaintenanceTicketForm(initial=initial, user=request.user)

    return render(request, 'assets/raise_ticket.html', {'form': form, 'asset': asset})
@login_required
def ticket_list(request):
    user = request.user

    if is_admin(user):
        tickets = MaintenanceTicket.objects.all().order_by('-date_reported')
    else:
        tickets = MaintenanceTicket.objects.filter(reported_by=user).order_by('-date_reported')

    context = {
        'tickets': tickets,
        'open_tickets': tickets.filter(status='Open'),
        'in_progress': tickets.filter(status='In Progress'),
        'resolved': tickets.filter(status='Resolved'),
        'closed': tickets.filter(status='Closed'),
    }
    return render(request, 'assets/ticket_list.html', context)


@login_required
def ticket_detail(request, pk):
    ticket = get_object_or_404(MaintenanceTicket, pk=pk)

    if not is_admin(request.user) and ticket.reported_by != request.user:
        messages.error(request, "You don't have permission to view this ticket.")
        return redirect('ticket_list')

    return render(request, 'assets/ticket_detail.html', {
        'ticket': ticket,
        'is_admin': is_admin(request.user),  
    })
# ==================== TICKET WORKFLOW VIEWS ====================

@login_required
@user_passes_test(is_admin)
def assign_technician(request, pk):
    ticket = get_object_or_404(MaintenanceTicket, pk=pk)
    technicians = User.objects.filter(is_staff=True)

    if request.method == "POST":
        technician_id = request.POST.get('technician')
        notes = request.POST.get('notes', '')

        if technician_id:
            ticket.assigned_to = get_object_or_404(User, id=technician_id)
            ticket.status = "Assigned"
            ticket.assignment_notes = notes
            ticket.date_assigned = timezone.now()
            ticket.asset.status = "Under Repair"
            ticket.asset.save()
            ticket.save()
            messages.success(request, "Technician assigned successfully!")
            return redirect('ticket_detail', pk=ticket.pk)

    context = {'ticket': ticket, 'technicians': technicians}
    return render(request, 'assets/ticket_assign_tech.html', context)



@login_required
@user_passes_test(is_admin)
def request_replacement(request, pk):
    ticket = get_object_or_404(MaintenanceTicket, pk=pk)

    if request.method == "POST":
        reason = request.POST.get('reason')
        estimated_cost = request.POST.get('estimated_cost')

        if reason:
            ticket.status = "Replacement Requested"
            ticket.replacement_reason = reason
            ticket.estimated_cost = estimated_cost or 0
            ticket.asset.status = "Replacement Required"
            ticket.asset.save()
            ticket.save()
            messages.warning(request, "Replacement request submitted to Finance.")
            return redirect('ticket_detail', pk=ticket.pk)

    return render(request, 'assets/ticket_request_replacement.html', {'ticket': ticket})


@login_required
@user_passes_test(is_admin)
def resolve_ticket(request, pk):
    ticket = get_object_or_404(MaintenanceTicket, pk=pk)

    if request.method == "POST":
        resolution_notes = request.POST.get('resolution_notes', '')
        ticket.status = "Resolved"
        ticket.resolved_by = request.user
        ticket.date_resolved = timezone.now()
        ticket.resolution_notes = resolution_notes
        if ticket.asset:
            ticket.asset.status = "Working"
            ticket.asset.save()
        ticket.save()
        messages.success(request, f'Ticket #{ticket.id} has been successfully resolved!')
        return redirect('ticket_detail', pk=ticket.pk)

    return render(request, 'assets/ticket_resolve.html', {'ticket': ticket})


# ====================== FINANCE VIEWS ======================
@login_required
@user_passes_test(is_admin)
def finance_approval_list(request):
    requests = MaintenanceTicket.objects.filter(
        status="Replacement Requested"
    ).order_by('-date_reported')
    context = {'requests': requests}
    return render(request, 'assets/finance_approval_list.html', context)


@login_required
@user_passes_test(is_admin)
def finance_approval_detail(request, pk):
    ticket = get_object_or_404(MaintenanceTicket, pk=pk)

    if request.method == "POST":
        decision = request.POST.get('decision')
        if decision == 'approve':
            ticket.finance_approved = True
            ticket.status = "Closed"
            ticket.asset.status = "Replaced"
            messages.success(request, "Replacement Approved & Asset Updated!")
        else:
            ticket.status = "Replacement Rejected"
            messages.error(request, "Replacement Request Rejected.")

        ticket.asset.save()
        ticket.save()
        return redirect('finance_approval_list')

    return render(request, 'assets/finance_approval_detail.html', {'ticket': ticket})


# ====================== REPORTS & USERS ======================
@login_required
def reports(request):
    user = request.user
    department = get_user_department(user)

    if is_admin(user):
        assets = Asset.objects.all()
        tickets = MaintenanceTicket.objects.all()
    else:
        assets = Asset.objects.filter(department=department) if department else Asset.objects.none()
        tickets = MaintenanceTicket.objects.filter(reported_by=user)

    context = {
        'total_assets': assets.count(),
        'working': assets.filter(status='Working').count(),
        'outdated': assets.filter(status='Replacement Required').count(),
        'lost': assets.filter(status__in=['Lost', 'Damaged']).count(),
        'recent_assets': assets.order_by('-id')[:5],
        'recent_tickets': tickets.order_by('-date_reported')[:10],
    }
    return render(request, 'assets/reports.html', context)


@login_required
@user_passes_test(is_admin)
def users_list(request):
    users = User.objects.all().order_by('-date_joined')
    context = {'users': users}
    return render(request, 'assets/users.html', context)