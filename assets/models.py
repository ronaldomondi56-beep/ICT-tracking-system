from django.db import models
from django.utils import timezone


class Asset(models.Model):
    name = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=100, unique=True)
    department = models.CharField(max_length=100)
    status = models.CharField(max_length=50, default="Working")
    purchase_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.serial_number})"

    class Meta:
        ordering = ['-id']


class MaintenanceTicket(models.Model):
    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
        ('Closed', 'Closed'),
    ]

    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
        ('Urgent', 'Urgent'),
    ]

    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='tickets')
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    reported_by = models.CharField(max_length=100, help_text="Name of person reporting")
    department = models.CharField(max_length=100)
    
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='Medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Open')
    
    date_reported = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    
    assigned_to = models.CharField(max_length=100, blank=True, null=True, help_text="Technician name")
    resolution_notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Ticket #{self.id} - {self.asset.name} ({self.status})"

    class Meta:
        ordering = ['-date_reported']