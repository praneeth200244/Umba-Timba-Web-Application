from django import forms

from accounts.validators import allow_only_images_validator 
from .models import User, UserProfile

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'phone_number', 'password']

    def clean(self):
        cleaned_data = super(UserForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        # To validate non field errors
        if password != confirm_password:
            raise forms.ValidationError(
                "Passwords doesn't match!"
            )
        
class UserProfileForm(forms.ModelForm):
    # To apply css class for fields and apply custom validators
    address = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Start typing....', 'required':'required'}))
    profile_picture = forms.FileField(widget=forms.FileInput(attrs={'class': 'btn btn-info'}), validators=[allow_only_images_validator])
    cover_photo = forms.FileField(widget=forms.FileInput(attrs={'class': 'btn btn-info'}), validators=[allow_only_images_validator])

    # To make latitude and longitude fields readonly
    # latitude = forms.CharField(widget = forms.TextInput(attrs={'readonly': 'readonly'}))
    # longitude = forms.CharField(widget = forms.TextInput(attrs={'readonly': 'readonly'}))

    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'cover_photo', 'address', 'country', 'state', 'city', 'pin_code', 'latitude', 'longitude']
    
    # To make latitude and longitude fields readonly (standard approach)
    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            if field == 'latitude' or field == 'longitude':
                self.fields[field].widget.attrs['readonly'] = 'readonly'

class UserInformationUpdationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number']