from django.urls import path
from .views import RegisterView,home,LoginView,LogoutView,set_default_address,SellerDashboardView,SellerLoginView,addproduct,product_detail
from .views import delete_product,edit_product,ProductListView
from . import views
from .views import SellerRegisterView


urlpatterns = [
    path('register/',RegisterView.as_view(),name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout',LogoutView.as_view(),name='logout'),
    path('delete_address/<int:address_id>/', views.DeleteAddressView.as_view(), name='delete_address'),
    path('set-default/<int:address_id>/', set_default_address, name='set_default_address'),
    path("seller/register/", SellerRegisterView.as_view(), name="seller_register"),
    path("seller/dashboard/", SellerDashboardView.as_view(), name="seller_dashboard"),
    path("seller/login/", SellerLoginView.as_view(), name="seller_login"),
    path("product/add/", addproduct, name="add_product"),
    path("products/", ProductListView.as_view(), name="product-list"),
     path('browse-products/', views.products_page, name='products_page'),
    path("product/detail/<int:product_id>/", product_detail, name="product_detail"),
    path("product/delete/<int:product_id>/", delete_product, name="delete_product"),
    path("product/edit/<int:product_id>/", edit_product, name="edit_product"),
    path('',home,name='home'),
]
