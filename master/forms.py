from django.contrib.auth.forms import AuthenticationForm,UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db.models import Q
from user.models import *
from django import forms

class LoginForm(forms.Form):
    user = forms.CharField(max_length=150,required=True)
    password = forms.CharField(widget=forms.PasswordInput,required=True)

    def clean(self):
        cleaned_data = super().clean()
        user = cleaned_data.get("user")
        password = cleaned_data.get("password")
        if user and password:
            user_obj = User.objects.using('default').filter(Q(username=user) | Q(email=user)).first()
            if user_obj:
               username = user_obj.username
               user = authenticate(username=username , password=password)
            
               if user is None:
                  raise forms.ValidationError("Invalid username or password")
               elif not user.is_active:
                  raise forms.ValidationError("This account is inactive")
               else:
                  cleaned_data["user"] = user  # store user for later use
               return cleaned_data
            else:
               raise forms.ValidationError("User not exist") 


class RegisterForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already in use")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already in use")
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])  # 👈 hash the password
        if commit:
            user.save()
        return user



class MenuForm(forms.Form):
    menu = forms.CharField(required=True)
    type = forms.CharField(required=True)
    link = forms.CharField(required=False)  # optional by default

    def clean(self):
        cleaned_data = super().clean()
        type_val = cleaned_data.get("type")
        link = cleaned_data.get("link")

        if type_val == "1" and not link:
            self.add_error("link", "Link is required when type is 1")

        return cleaned_data


class PostForm(forms.Form):
    name = forms.CharField(required=True)
    rate = forms.CharField(required=True)
    size = forms.CharField(required=True)  
    lang = forms.CharField(required=True)  
    image = forms.CharField(required=True)  
    genre = forms.CharField(required=True)  
    starcast = forms.CharField(required=True)  
    status = forms.CharField(required=True)  
    release_date = forms.CharField(required=True)  
    duration = forms.CharField(required=True)  
    menu = forms.CharField(required=True)  
    story = forms.CharField(required=True)  

           