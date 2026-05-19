from django import forms
from .models import Asset, MaintenanceTicket


class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = ['name', 'serial_number', 'department', 'status', 'purchase_date', 'notes']
        widgets = {
            'purchase_date': forms.DateInput(attrs={'type': 'date'}),
        }


class MaintenanceTicketForm(forms.ModelForm):
    class Meta:
        model = MaintenanceTicket
        fields = ['title', 'description', 'reported_by', 'department', 'priority']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'title': forms.TextInput(attrs={'placeholder': 'e.g. No display, Slow performance, etc.'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['reported_by'].widget.attrs.update({'placeholder': 'Your Full Name'})
        self.fields['department'].widget.attrs.update({'placeholder': 'Your Department'})