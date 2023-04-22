from django.forms import ModelForm
from .models import *
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import SetPasswordForm, PasswordResetForm


# Form for adding new Item
class AddItemForm(ModelForm):
    class Meta:
        model = Item
        exclude = [
            "category",
            "item_type",
            "quantity_unit",
            "location",
            "quantity",
            "item_code",
            "min_alert_quantity",
            "qr_code",
            "holder",
            "status",
            "vendor",
            "department"]

    date_received = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}), )
    expiration_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}), required=False)

    def __init__(self, *args, **kwargs):
        super(AddItemForm, self).__init__(*args, **kwargs)

        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

            if visible.field.label == "Image":
                visible.field.widget.attrs['class'] = 'form-control d-none'

            if visible.field.label == "Notes" or visible.field.label == "Description":
                visible.field.widget.attrs['rows'] = 6


# Form for adding items in bulk and consumables
class AddAccessoryForm(ModelForm):
    class Meta:
        model = Item
        exclude = [
            "category",
            "item_type",
            "location",
            "item_code",
            "qr_code",
            "holder",
            "status",
            "vendor",
            "department"]

    date_received = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}))
    expiration_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}), required=False)

    def __init__(self, *args, **kwargs):
        super(AddAccessoryForm, self).__init__(*args, **kwargs)

        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

            if visible.field.label == "Image":
                visible.field.widget.attrs['class'] = 'form-control d-none'

            if visible.field.label == "Notes" or visible.field.label == "Description":
                visible.field.widget.attrs['rows'] = 6


# For Licenses
class AddLicenseForm(ModelForm):
    class Meta:
        model = License
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(AddLicenseForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'


# Registration form
class CustomUserCreationForm(UserCreationForm):
    # email = UCAEmailField(label=_('Email'), max_length=254)

    class Meta:
        fields = ('email', 'password1', 'password2')
        model = get_user_model()

    email = forms.CharField(widget=forms.EmailInput(attrs={'placeholder': 'Email',
                                                           'class': 'form-control',
                                                           }))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password',
                                                                  'class': 'form-control',
                                                                  }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password',
                                                                  'class': 'form-control',
                                                                  }))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password2'].label = "Confirm Password"
        self.fields['password1'].label = "Password"


class SetPasswordForm(SetPasswordForm):
    class Meta:
        model = get_user_model()
        fields = ['new_password1', 'new_password2']

    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'New password',
                                                                      'class': 'form-control',
                                                                      }))
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm new password',
                                                                      'class': 'form-control',
                                                                      }))


class PasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super(PasswordResetForm, self).__init__(*args, **kwargs)

    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email',
                                                            'class': 'form-control',
                                                            }))


class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        exclude = ['owner']

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)

        for visible in self.visible_fields():

            if visible.field.label == "Profile pic":
                visible.field.widget.attrs['class'] = 'form-control d-none'


class CategoryForm(ModelForm):
    class Meta:
        model = Category
        exclude = ['department']

    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)

        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            if visible.field.label == "Description":
                visible.field.widget.attrs['rows'] = 5
