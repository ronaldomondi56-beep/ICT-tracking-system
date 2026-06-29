from django import forms
from .models import Asset, MaintenanceTicket


class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = [
            'name',
            'serial_number',
            'department',
            'status',
            'purchase_date',
            'notes'
        ]

        widgets = {
            'purchase_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    STATUS_CHOICES = [
        ('Working', 'Working'),
        ('Under Repair', 'Under Repair'),
        ('Replacement Required', 'Replacement Required'),
        ('Replaced', 'Replaced'),
        ('Lost', 'Lost'),
        ('Damaged', 'Damaged'),
    ]

    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        widget=forms.Select(
            attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl'
            }
        )
    )


class MaintenanceTicketForm(forms.ModelForm):
    class Meta:
        model = MaintenanceTicket

        fields = [
            'title',
            'description',
            'reported_by',
            'department',
            'priority'
        ]

        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'title': forms.TextInput(
                attrs={
                    'placeholder': 'e.g. No display, Printer failure, Network issue'
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['reported_by'].widget.attrs.update({
            'placeholder': 'Your Full Name'
        })

        self.fields['department'].widget.attrs.update({
            'placeholder': 'Department'
        })