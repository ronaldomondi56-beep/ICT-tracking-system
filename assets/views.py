from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone

from .models import Asset, MaintenanceTicket
from .forms import AssetForm, MaintenanceTicketForm


# ====================== HELPER FUNCTIONS ======================
def is_admin(user):
    """Check if user is Admin"""
    return user.is_superuser or user.is_staff


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


# ====================== DASHBOARD ======================
@login_required
def dashboard(request):
    total_assets = Asset.objects.count()
    working = Asset.objects.filter(status='Working').count()
    outdated = Asset.objects.filter(status='Replacement Required').count()
    lost_damaged = Asset.objects.filter(status__in=['Lost', 'Damaged']).count()

    # Ticket Metrics
    total_tickets = MaintenanceTicket.objects.count()
    open_tickets = MaintenanceTicket.objects.filter(status='Open').count()
    assigned_tickets = MaintenanceTicket.objects.filter(status='Assigned').count()
    in_progress = MaintenanceTicket.objects.filter(status='In Progress').count()
    resolved = MaintenanceTicket.objects.filter(status='Resolved').count()
    closed = MaintenanceTicket.objects.filter(status='Closed').count()

    recent_assets = Asset.objects.all().order_by('-id')[:5]
    recent_tickets = MaintenanceTicket.objects.all().order_by('-date_reported')[:5]

    context = {
        'total_assets': total_assets,
        'working': working,
        'outdated': outdated,
        'lost': lost_damaged,

        'total_tickets': total_tickets,
        'open_tickets': open_tickets,
        'assigned_tickets': assigned_tickets,
        'in_progress': in_progress,
        'resolved': resolved,
        'closed': closed,

        'recent_assets': recent_assets,
        'recent_tickets': recent_tickets,
        'is_admin': is_admin(request.user),
    }

    return render(request, 'assets/dashboard.html', context)


# ====================== ASSET MANAGEMENT ======================
@login_required
def assetlist(request):
    assets = Asset.objects.all().order_by('-id')
    
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
    
    department_filter = request.GET.get('department', '')
    if department_filter:
        assets = assets.filter(department=department_filter)

    context = {
        'assets': assets,
        'search_query': search_query,
        'status_filter': status_filter,
        'department_filter': department_filter,
        'is_admin': is_admin(request.user),
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
            return redirect('asset_list')
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
    asset = get_object_or_404(Asset, pk=asset_pk) if asset_pk else None
    
    if request.method == "POST":
        form = MaintenanceTicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            if asset:
                ticket.asset = asset
            ticket.reported_by = request.user.username
            ticket.save()
            messages.success(request, f'Ticket #{ticket.id} raised successfully!')
            return redirect('ticket_list')
    else:
        initial = {'reported_by': request.user.username}
        if asset:
            initial.update({
                'department': asset.department,
                'title': f'Issue with {asset.name}'
            })
        form = MaintenanceTicketForm(initial=initial)

    return render(request, 'assets/raise_ticket.html', {'form': form, 'asset': asset})


@login_required
def ticket_list(request):
    tickets = MaintenanceTicket.objects.all().order_by('-date_reported')
    
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
    return render(request, 'assets/ticket_detail.html', {'ticket': ticket})


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
def start_repair(request, pk):
    ticket = get_object_or_404(MaintenanceTicket, pk=pk)

    if request.method == "POST":
        ticket.status = "In Progress"
        ticket.date_started = timezone.now()
        ticket.save()

        if ticket.asset:
            ticket.asset.status = "Under Repair"
            ticket.asset.save()

        messages.success(request, f"Repair started on Ticket #{ticket.id}!")
        return redirect('ticket_detail', pk=ticket.pk)

    context = {'ticket': ticket}
    return render(request, 'assets/ticket_start_repair.html', context)


@login_required
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

    context = {'ticket': ticket}
    return render(request, 'assets/ticket_request_replacement.html', context)


# ====================== NEW: RESOLVE TICKET ======================
@login_required
@user_passes_test(is_admin)
def resolve_ticket(request, pk):
    """Mark a ticket as Resolved"""
    ticket = get_object_or_404(MaintenanceTicket, pk=pk)

    if request.method == "POST":
        resolution_notes = request.POST.get('resolution_notes', '')

        ticket.status = "Resolved"
        ticket.resolved_by = request.user
        ticket.date_resolved = timezone.now()
        ticket.resolution_notes = resolution_notes
        
        # Restore asset status to working
        if ticket.asset:
            ticket.asset.status = "Working"
            ticket.asset.save()

        ticket.save()

        messages.success(request, f'Ticket #{ticket.id} has been successfully resolved!')
        return redirect('ticket_detail', pk=ticket.pk)

    # GET request - show resolution form
    context = {'ticket': ticket}
    return render(request, 'assets/ticket_resolve.html', context)


# ====================== FINANCE VIEWS ======================
@login_required
@user_passes_test(is_admin)
def finance_approval_list(request):
    requests = MaintenanceTicket.objects.filter(status="Replacement Requested").order_by('-date_reported')
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

    context = {'ticket': ticket}
    return render(request, 'assets/finance_approval_detail.html', context)


# ====================== REPORTS & USERS ======================
@login_required
def reports(request):
    context = {
        'total_assets': Asset.objects.count(),
        'working': Asset.objects.filter(status='Working').count(),
        'outdated': Asset.objects.filter(status='Replacement Required').count(),
        'lost': Asset.objects.filter(status__in=['Lost', 'Damaged']).count(),
        'recent_assets': Asset.objects.all().order_by('-id')[:5],
        'recent_tickets': MaintenanceTicket.objects.all().order_by('-date_reported')[:10],
    }
    return render(request, 'assets/reports.html', context)


@login_required
@user_passes_test(is_admin)
def users_list(request):
    users = User.objects.all().order_by('-date_joined')
    context = {'users': users}
    return render(request, 'assets/users.html', context)


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Account created successfully for {user.username}!")
            return redirect('login')
    else:
        form = UserCreationForm()

    return render(request, 'assets/register.html', {'form': form})