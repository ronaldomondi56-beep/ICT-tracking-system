from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib import messages

from .models import Asset, MaintenanceTicket
from .forms import AssetForm, MaintenanceTicketForm


# ====================== DASHBOARD ======================
def dashboard(request):
    """Main dashboard with statistics"""
    total_assets = Asset.objects.count()
    
    working = Asset.objects.filter(status='Working').count()
    outdated = Asset.objects.filter(status='Outdated').count()
    lost_damaged = Asset.objects.filter(
        status__in=['Lost', 'Damaged', 'Lost display', 'lost', 'damaged']
    ).count()
    
    recent_assets = Asset.objects.all().order_by('-id')[:5]

    context = {
        'total_assets': total_assets,
        'working': working,
        'outdated': outdated,
        'lost': lost_damaged,
        'recent_assets': recent_assets,
    }
    
    return render(request, 'assets/dashboard.html', context)


# ====================== ASSET LIST ======================
def assetlist(request):
    """Display all assets with search and filter"""
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
    }
    
    return render(request, 'assets/assetlist.html', context)


# ====================== ADD ASSET ======================
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


# ====================== EDIT & DELETE ASSET ======================
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


def asset_delete(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    if request.method == "POST":
        asset_name = asset.name
        asset.delete()
        messages.success(request, f'Asset "{asset_name}" deleted successfully!')
        return redirect('asset_list')
    
    return render(request, 'assets/asset_confirm_delete.html', {'asset': asset})


# ====================== TICKETING SYSTEM ======================

# Raise New Ticket
def raise_ticket(request, asset_pk):
    asset = get_object_or_404(Asset, pk=asset_pk)
    
    if request.method == "POST":
        form = MaintenanceTicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.asset = asset
            ticket.save()
            messages.success(request, f'Ticket raised successfully for {asset.name}!')
            return redirect('ticket_list')
    else:
        form = MaintenanceTicketForm(initial={
            'department': asset.department,
            'reported_by': 'Staff'  
        })

    return render(request, 'assets/raise_ticket.html', {
        'form': form,
        'asset': asset
    })


# All Tickets List
def ticket_list(request):
    tickets = MaintenanceTicket.objects.all()
    context = {'tickets': tickets}
    return render(request, 'assets/ticket_list.html', context)


# Ticket Detail
def ticket_detail(request, pk):
    ticket = get_object_or_404(MaintenanceTicket, pk=pk)
    context = {'ticket': ticket}
    return render(request, 'assets/ticket_detail.html', context)
# ====================== UPDATE TICKET ======================
def ticket_update(request, pk):
    ticket = get_object_or_404(MaintenanceTicket, pk=pk)

    if request.method == "POST":
        form = MaintenanceTicketForm(request.POST, instance=ticket)

        if form.is_valid():
            form.save()
            messages.success(request, "Ticket updated successfully!")
            return redirect('ticket_detail', pk=ticket.pk)

    else:
        form = MaintenanceTicketForm(instance=ticket)

    return render(request, 'assets/raise_ticket.html', {
        'form': form,
        'ticket': ticket
    })


# ====================== REPORTS ======================
def reports(request):
    return render(request, 'assets/reports.html')


# ====================== USERS ======================
def users_list(request):
    return render(request, 'assets/users.html')