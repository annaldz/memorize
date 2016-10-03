from django.contrib.auth.models import User
from django import forms
from django.core.validators import MinLengthValidator
from django.contrib.auth.forms import PasswordChangeForm

class UserForm(forms.ModelForm):
    password = forms.CharField(
          widget=forms.PasswordInput(),
          validators=[
              MinLengthValidator(8)
          ]
    )
    email = forms.EmailField()
    first_name = forms.CharField()
    last_name = forms.CharField()
   
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password')

class ProfileAlterForm(forms.ModelForm):
    email = forms.EmailField()
    first_name = forms.CharField()
    last_name = forms.CharField()
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')

     
