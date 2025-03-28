from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import AppUser,Address,Seller,Product,Tag
from django.core.exceptions import ValidationError
import requests

class AppUserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=15,required=False)
    street = forms.CharField(max_length=255, required=False)
    city = forms.CharField(max_length=100, required=False)
    state = forms.CharField(max_length=100, required=False)
    postal_code = forms.CharField(max_length=20, required=False)
    country = forms.CharField(max_length=100, required=False)
    is_default = forms.BooleanField(required=False)
    class Meta:
        model = AppUser
        fields = ['username','email','phone_number','street','city','state','postal_code','country','is_default','password1','password2']
        
    def clean_postal_code(self):
        postal_code = self.cleaned_data.get('postal_code')
        if postal_code:
            if not postal_code.isdigit():
                raise ValidationError("Postal code must contain only digits.")
            if len(postal_code) != 6:
                raise ValidationError("Postal code must be 6 digits.")
        return postal_code

    def clean(self):
        cleaned_data = super().clean()
        postal_code = cleaned_data.get('postal_code')
        if postal_code:
            try:
                response = requests.get(f"https://api.postalpincode.in/pincode/{postal_code}")
                response.raise_for_status()
                data = response.json()
                if data and data[0]['Status'] == "Success":
                    cleaned_data['city'] = data[0]['PostOffice'][0]['District']
                    cleaned_data['state'] = data[0]['PostOffice'][0]['State']

            except requests.exceptions.RequestException as e:
               
                self.add_error('postal_code', f"Error fetching city/state: {e}")
            except (KeyError, IndexError):
             
                self.add_error('postal_code', "Invalid postal code or API error.")

        return cleaned_data
        
class LoginForm(forms.Form):
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    
class AddressForm(forms.ModelForm):
    class Meta:
        model=Address
        fields=['street','city','state','postal_code','country','is_default']
        
    def clean_postal_code(self):
        postal_code = self.cleaned_data.get('postal_code')
        if postal_code:
            if not postal_code.isdigit():
                 raise ValidationError("Postal code must contain only digits.")
            if len(postal_code) != 6:
                raise ValidationError("Postal code must be 6 digits.")
        return postal_code

    def clean(self):
        cleaned_data = super().clean()
        postal_code = cleaned_data.get('postal_code')
        if postal_code:
            try:
                response = requests.get(f"https://api.postalpincode.in/pincode/{postal_code}")
                response.raise_for_status()
                data = response.json()
                if data and data[0]['Status'] == "Success":
                    cleaned_data['city'] = data[0]['PostOffice'][0]['District']
                    cleaned_data['state'] = data[0]['PostOffice'][0]['State']

            except requests.exceptions.RequestException as e:
                self.add_error('postal_code', f"Error fetching city/state: {e}")
            except (KeyError, IndexError):
                self.add_error('postal_code', "Invalid postal code or API error.")

        return cleaned_data
    

class SellerRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")
    class Meta:
        model=Seller
        fields=['store_name','phone_number','gst_number','email']
        
    def clean_gst_number(self):
        gst_number = self.cleaned_data.get('gst_number')
        if gst_number:
            if not gst_number.isdigit():
                raise ValidationError("GST number must contain only digits.")
            if len(gst_number) != 15:
                raise ValidationError("GST number must be 15 digits.")
        return gst_number
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")  
            
        return cleaned_data
    
    def save(self,commit=True):
        user=AppUser.objects.create_user(username=self.cleaned_data['store_name'],email=self.cleaned_data['email'],password=self.cleaned_data['password'])
          # ✅ Create Seller instance and link it to the user
        seller = Seller(
        user=user,
        store_name=self.cleaned_data['store_name'],
        phone_number=self.cleaned_data['phone_number'],
        gst_number=self.cleaned_data['gst_number'],
        email=self.cleaned_data['email']
        )
        if commit:
            seller.save()
        return seller
        

class ProductForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),  # ✅ Fetch from Tag model, not Product
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Product
        fields = ['name', 'category', 'price', 'description', 'image', 'stock', 'tags']
