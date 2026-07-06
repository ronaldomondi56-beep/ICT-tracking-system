from django.db import models
from django.contrib.auth.models import User


DEPARTMENT_CHOICES = [
    ('ICT', 'ICT'),
    ('Finance', 'Finance'),
    ('HR', 'Human Resources'),
    ('Administration Police', 'Administration Police'),
    ('Labour', 'Labour'),
    ('Procurement', 'Procurement'),
    ('TSE', 'TSE'),
    ('Naccada', 'Naccada'),
    ('Regional Commissioner', 'Regional Commissioner'),
    ('County commissioner', 'County commissioner'),
]

BLOCK_CHOICES = [
    ('A', 'Block A'),
    ('B', 'Block B'),
    ('C', 'Block C'),
    ('D', 'Block D'),
    ('E', 'Block E'),
    ('F', 'Block F'),
]

FLOOR_CHOICES = [
    ('Ground', 'Ground Floor'),
    ('1st', '1st Floor'),
    ('2nd', '2nd Floor'),
    ('3rd', '3rd Floor'),
    ('4th', '4th Floor'),
    ('5th', '5th Floor'),
]


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    department = models.CharField(max_length=100, choices=DEPARTMENT_CHOICES, blank=True)
    block = models.CharField(max_length=10, choices=BLOCK_CHOICES, blank=True)
    floor = models.CharField(max_length=20, choices=FLOOR_CHOICES, blank=True)
    office_name = models.CharField(max_length=100, blank=True)
    door_number = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.user.username} — {self.department}"


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
    department = models.CharField(max_length=100, choices=DEPARTMENT_CHOICES)

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='Working'
    )

    purchase_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name}"

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

    reported_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reported_tickets'
    )

    department = models.CharField(max_length=100, choices=DEPARTMENT_CHOICES)

    # Location fields
    office_name = models.CharField(max_length=100, blank=True)
    door_number = models.CharField(max_length=20, blank=True)
    block = models.CharField(max_length=10, choices=BLOCK_CHOICES, blank=True)
    floor = models.CharField(max_length=20, choices=FLOOR_CHOICES, blank=True)

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

    technician_report = models.TextField(blank=True, null=True)
    resolution_notes = models.TextField(blank=True, null=True)

    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_tickets'
    )

    replacement_reason = models.TextField(blank=True, null=True)

    estimated_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )

    procurement_approved = models.BooleanField(default=False)
    finance_approved = models.BooleanField(default=False)
    replacement_completed = models.BooleanField(default=False)

    date_resolved = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Ticket #{self.id} - {self.asset.name} ({self.status})"

    class Meta:
        ordering = ['-date_reported']