from django.db import models
from django.contrib.auth.models import User


class Asset(models.Model):
    STATUS_CHOICES = [
        ('Working', 'Working'),
        ('Under Repair', 'Under Repair'),
        ('Replacement Required', 'Replacement Required'),
        ('Replaced', 'Replaced'),
        ('Lost', 'Lost'),
        ('Damaged', 'Damaged'),
    ]

    name = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=100, unique=True)
    department = models.CharField(max_length=100)

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='Working'
    )

    purchase_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.serial_number})"

    class Meta:
        ordering = ['-id']


class MaintenanceTicket(models.Model):

    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('Assigned', 'Assigned'),
        ('In Progress', 'In Progress'),
        ('Replacement Required', 'Replacement Required'),
        ('Awaiting Procurement', 'Awaiting Procurement'),
        ('Awaiting Finance Approval', 'Awaiting Finance Approval'),
        ('Resolved', 'Resolved'),
        ('Closed', 'Closed'),
    ]

    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
        ('Urgent', 'Urgent'),
    ]

    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name='tickets'
    )

    title = models.CharField(max_length=200)
    description = models.TextField()

    reported_by = models.CharField(
        max_length=100,
        help_text="Name of person reporting"
    )

    department = models.CharField(max_length=100)

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='Medium'
    )

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='Open'
    )

    date_reported = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    # Technician assigned by admin
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tickets',
        help_text="Assigned Technician"
    )

    assignment_notes = models.TextField(blank=True, null=True)
    date_assigned = models.DateTimeField(blank=True, null=True)
    date_started = models.DateTimeField(blank=True, null=True)

    # Technician findings
    technician_report = models.TextField(
        blank=True,
        null=True
    )

    # Resolution notes
    resolution_notes = models.TextField(
        blank=True,
        null=True
    )

    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_tickets'
    )

    # Replacement workflow
    replacement_reason = models.TextField(
        blank=True,
        null=True
    )

    estimated_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )

    procurement_approved = models.BooleanField(default=False)
    finance_approved = models.BooleanField(default=False)

    replacement_completed = models.BooleanField(default=False)

    date_resolved = models.DateTimeField(
        blank=True,
        null=True
    )

    def __str__(self):
        return f"Ticket #{self.id} - {self.asset.name} ({self.status})"

    class Meta:
        ordering = ['-date_reported']