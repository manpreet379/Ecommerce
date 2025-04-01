from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer 
from django.views.generic import TemplateView
from django.contrib.auth import login, authenticate,logout
from .forms import AppUserRegisterForm, LoginForm,SellerRegisterForm,AddressForm,ProductForm
from .models import AppUser, Address, Seller, Product
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .paginations import CustomPagination
from .serializers import ProductSerializer
import random


class RegisterView(View):
    def get(self, request):
        form = AppUserRegisterForm()
        return render(request, "services/register.html", {"form": form})

    def post(self, request):
        form = AppUserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  
            user.set_password(form.cleaned_data["password1"])  
            user.save()  
            
            # Create an Address instance if address fields were filled
            if form.cleaned_data['street'] or form.cleaned_data['city'] or form.cleaned_data['state'] or form.cleaned_data['postal_code'] or form.cleaned_data['country']:
                Address.objects.create(
                    user=user,
                    street=form.cleaned_data['street'],
                    city=form.cleaned_data['city'],
                    state=form.cleaned_data['state'],
                    postal_code=form.cleaned_data['postal_code'],
                    country=form.cleaned_data['country'],
                    is_default = form.cleaned_data['is_default']
                )
           
            user = authenticate(request, email=user.email, password=form.cleaned_data["password1"])
            if user is not None:
                login(request, user)
                return redirect("home")

        return render(request, "services/register.html", {"form": form})



class SellerRegisterView(View):
    def get(self, request):
        form = SellerRegisterForm()
        return render(request, "seller/seller_register.html", {"form": form})

    def post(self, request):
        form = SellerRegisterForm(request.POST)
        if form.is_valid():
            seller = form.save(commit=True)  
            user = authenticate(request, email=seller.user.email, password=form.cleaned_data["password"])
            if user is not None:
                login(request, user)
                return redirect("seller_dashboard")  
        return render(request, "seller/seller_register.html", {"form": form})

    

class SellerDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "seller/seller_dashboard.html"

    def get(self, request, *args, **kwargs):
        try:
            seller = request.user.seller_profile  # Try to get the linked Seller instance
            print("Seller exists:", seller)  # Debugging
        except AttributeError:
            print("User has no seller profile:", request.user)  # Debugging
            messages.error(request, "You are not registered as a seller.")
            return redirect("home")  # Redirect non-sellers to home

        return render(request, self.template_name, {"seller": seller})

class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:  
            return redirect("home")  
        form = LoginForm()
        
        return render(request, "services/login.html", {"form": form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            user = authenticate(request, email=email, password=password)  # Authenticate directly
            if user is not None:
                
                login(request, user)
                if hasattr(user, "seller_profile"):
                    return redirect("seller_dashboard")
                return redirect("home")
            else:
                form.add_error(None, "Invalid email or password")

        return render(request, "services/login.html", {"form": form})


class SellerLoginView(View):
    def get(self, request):
        if request.user.is_authenticated and hasattr(request.user, "seller_profile"):
            return redirect("seller_dashboard")
        form = LoginForm()
        return render(request, "seller/seller_login.html", {"form": form})
    
    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user = authenticate(request, email=email, password=password)
            if user is not None and hasattr(user, "seller_profile"):
                login(request, user)
                return redirect("seller_dashboard")
            else:
                form.add_error(None, "Invalid email or password")
        return render(request, "seller/seller_login.html", {"form": form})

class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("home")
    
class DeleteAddressView(View):
    def post(self, request, address_id):
        address = get_object_or_404(Address, id=address_id, user=request.user)
        address.delete()
        remaining_addresses = Address.objects.filter(user=request.user)
        if remaining_addresses.count() == 1:
            last_address = remaining_addresses.first()
            last_address.is_default = True
            last_address.save()

        return redirect('home') 
    
    
def home(request):
    addresses = Address.objects.filter(user=request.user) if request.user.is_authenticated else None
    address_form = AddressForm() if request.user.is_authenticated else None
    # selected_products = []
    # if request.user.is_authenticated :
    #     selected_products = Product.objects.order_by('?')[:10]  # Fetch 10 random products
    #     print("Selected products:", selected_products) 
    #     dell_product = Product.objects.get(name="dell")

    # Print the image URL to the console (VS Code terminal)
        # if dell_product.image:
        #     print("Dell product image URL:", dell_product.image.url)# Debugging

    if request.method == "POST" and request.user.is_authenticated:
        address_form = AddressForm(request.POST)
        if address_form.is_valid():
            address = address_form.save(commit=False)
            address.user = request.user
            address.save()
            return redirect('home')

    return render(request, "services/home.html", {
        "addresses": addresses,
        "address_form": address_form,
         # Pass random products to the template
    })
@login_required
def set_default_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    
    # Set the selected address as default
    Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
    address.is_default = True
    address.save()

    return redirect('home')  


@login_required
def addproduct(request):
    seller = get_object_or_404(Seller, user=request.user)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = seller
            product.save()
            form.save_m2m()
            return redirect('seller_dashboard')
    else:
        form = ProductForm()
    return render(request, 'seller/add_product.html', {'form': form})


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    related_products = product.get_related_products()
    return render(request, "products/product_detail.html", {"product": product, "related_products": related_products})


@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, seller=request.user.seller_profile)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('seller_dashboard')
    else:
        form = ProductForm(instance=product)

    return render(request, 'seller/edit_product.html', {'form': form, 'product': product})

@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, seller=request.user.seller_profile)
    if request.method == 'POST':
        product.delete()
        return redirect('seller_dashboard')

    return render(request, 'seller/delete_product.html', {'product': product})



## Product views:


class ProductListView(APIView):
    
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    renderer_classes = [JSONRenderer] 
    
    def get(self,request,format=None):
        
        category = request.GET.get('category')
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        search = request.GET.get('search')
        sort_by = request.GET.get('sort_by')
        
        products = Product.objects.all()
        
        if category:
            products = products.filter(category=category)
        if min_price:
            products = products.filter(price__gte=min_price)
        if max_price:
            products = products.filter(price__lte=max_price)
        if search:
            products = products.filter(name__icontains=search)
        if sort_by:
            products = products.order_by(sort_by)
            
        paginator = CustomPagination()
        paginated_products = paginator.paginate_queryset(products, request)
        
        serialized_products = ProductSerializer(paginated_products, many=True)
        return Response(serialized_products.data)
    
    
@login_required
def products_page(request):
    # Get a random selection of products
    if request.user.is_authenticated:
        products = Product.objects.all()
        random_products = random.sample(list(products), min(5, len(products)))  # Get up to 5 random products
        return render(request, 'services/products.html', {'products': random_products})
    
   