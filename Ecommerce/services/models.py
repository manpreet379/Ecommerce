from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
class AppUser(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15,blank=True,null=True)
    
    
    USERNAME_FIELD = "email"  
    REQUIRED_FIELDS = ["username"]  #requried whern creating supoeruser
    
    
    def __str__(self):
        return self.username

class Address(models.Model):
    user=models.ForeignKey(AppUser,on_delete=models.CASCADE, related_name="addresses")
    street=models.CharField(max_length=255,blank=True,null=True)
    city=models.CharField(max_length=255,blank=True,null=True)
    state=models.CharField(max_length=255,blank=True,null=True)
    postal_code=models.CharField(max_length=255,blank=True,null=True)
    country=models.CharField(max_length=255,blank=True,null=True)
    is_default=models.BooleanField(default=False)
    
    
    
    def save(self, *args, **kwargs):
        if self.is_default:
            # Ensure no other address is default
            Address.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.street}, {self.city}, {self.state}, {self.postal_code}, {self.country}"
    
    
class Seller(models.Model):
    user=models.OneToOneField(AppUser,on_delete=models.CASCADE,related_name='seller_profile')
    store_name=models.CharField(max_length=255,unique=True)
    phone_number=models.CharField(max_length=15)
    gst_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    email=models.EmailField()
    
    class Meta:
        verbose_name = "Seller"
        verbose_name_plural = "Sellers"
   
    
    def __str__(self):
        return self.store_name
    

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('laptop', 'Laptop'),
        ('mobile', 'Mobile'),
        ('headphone', 'Headphone'),
        ('smartwatch', 'Smartwatch'),
        ('speaker', 'Speaker'),
        ('accessories', 'Accessories'),
        ('keyboard', 'Keyboard'),
        ('mouse', 'Mouse'),
    ]

    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=255, choices=CATEGORY_CHOICES)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    tags = models.ManyToManyField(Tag, blank=True, related_name='products')  # ✅ FIXED

    
    def __str__(self):
        return self.name
    
    def get_related_products(self):
        return self.tags.all()[:5]