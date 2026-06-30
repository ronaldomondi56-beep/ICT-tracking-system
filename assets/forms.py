from django import forms
from .models import Asset, MaintenanceTicket


INPUT_CLASSES = (
    'w-full border-2 border-gray-200 rounded-xl px-4 py-3 text-base '
    'focus:outline-none focus:border-accent focus:ring-4 focus:ring-accent/15 transition'
)


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
            'name': forms.TextInput(attrs={'placeholder': 'e.g. Dell Latitude 5420'}),
            'serial_number': forms.TextInput(attrs={'placeholder': 'e.g. SN-2024-0098'}),
            'department': forms.TextInput(attrs={'placeholder': 'e.g. ICT Authority'}),
            'purchase_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Optional notes about this asset...'}),
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
        widget=forms.Select()
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            existing = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f"{INPUT_CLASSES} {existing}".strip()


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

        for field_name, field in self.fields.items():
            existing = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f"{INPUT_CLASSES} {existing}".strip()