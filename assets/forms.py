from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Asset, MaintenanceTicket, UserProfile, DEPARTMENT_CHOICES, BLOCK_CHOICES, FLOOR_CHOICES, TICKET_TYPE_CHOICES


INPUT_CLASSES = (
    'w-full border-2 border-gray-200 rounded-xl px-4 py-3 text-base '
    'focus:outline-none focus:border-accent focus:ring-4 focus:ring-accent/15 transition'
)


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=False)
    department = forms.ChoiceField(choices=[('', '-- Select Department --')] + list(DEPARTMENT_CHOICES))
    block = forms.ChoiceField(choices=[('', '-- Select Block --')] + list(BLOCK_CHOICES))
    floor = forms.ChoiceField(choices=[('', '-- Select Floor --')] + list(FLOOR_CHOICES))
    office_name = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'placeholder': 'e.g. ICT Office'}))
    door_number = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'placeholder': 'e.g. D-101'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            existing = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f"{INPUT_CLASSES} {existing}".strip()

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            UserProfile.objects.create(
                user=user,
                department=self.cleaned_data.get('department', ''),
                block=self.cleaned_data.get('block', ''),
                floor=self.cleaned_data.get('floor', ''),
                office_name=self.cleaned_data.get('office_name', ''),
                door_number=self.cleaned_data.get('door_number', ''),
            )
        return user


class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = ['name', 'department', 'status', 'purchase_date', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'e.g. Dell Latitude 5420'}),
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

    status = forms.ChoiceField(choices=STATUS_CHOICES, widget=forms.Select())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            existing = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f"{INPUT_CLASSES} {existing}".strip()


class MaintenanceTicketForm(forms.ModelForm):
    class Meta:
        model = MaintenanceTicket
        fields = [
            'ticket_type', 'asset', 'description', 'priority',
            'office_name', 'door_number', 'block', 'floor',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'office_name': forms.TextInput(attrs={'placeholder': 'e.g. ICT Office'}),
            'door_number': forms.TextInput(attrs={'placeholder': 'e.g. D-101'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        # Asset not required — network tickets don't need one
        self.fields['asset'].required = False

        # Filter assets by user's department
        if user and hasattr(user, 'profile') and user.profile.department:
            self.fields['asset'].queryset = Asset.objects.filter(
                department=user.profile.department
            )
        else:
            self.fields['asset'].queryset = Asset.objects.all()

        # Pre-fill all location fields from user profile
        if user and hasattr(user, 'profile'):
            profile = user.profile
            self.fields['office_name'].initial = profile.office_name
            self.fields['door_number'].initial = profile.door_number
            self.fields['block'].initial = profile.block
            self.fields['floor'].initial = profile.floor

        for field_name, field in self.fields.items():
            existing = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f"{INPUT_CLASSES} {existing}".strip()