from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import hashlib
import secrets


def hash_otp(otp:str, salt: str) -> str:
    return hashlib.sha256(f"{salt}{otp}" .encode()).hexdigest()

class OTPRequest(models.Model):
    TARGET_TYPE_CHOICES = (('email', 'email'), ('phone', 'phone'))

    target_type = models.CharField(max_length=10, choices=TARGET_TYPE_CHOICES)
    target_value = models.CharField(max_length=255)
    salt = models.CharField(max_length=32)
    otp_hash = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    attempts = models.IntegerField(default=0)
    verified = models.BooleanField(default=False)
    meta =models.JSONField(blank=True, null=True)

    def set_otp(self, otp_plain: str, valid_seconds: int = 300):
        self.salt = secrets.token_hex(16)
        self.otp_hash = hash_otp(otp_plain, self.salt)
        self.expires_at = timezone.now() + timezone.timedelta(seconds=valid_seconds)

    def check_otp(self, otp_plain: str):
        return self.otp_hash == hash_otp(otp_plain, self.salt)
    
    def is_expired(self):
        return timezone.now() > self.expires_at


# Create your models here.
class Contact(models.Model):
    msg_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    email = models.CharField(max_length=70, default="")
    phone = models.CharField(max_length=70, default="")
    desc = models.CharField(max_length=500, default="")
    def __str__(self):
        return self.name
    
    
class TeamMember(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='team/')  # images will go to media/team/
    role = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('groceries', 'Groceries'),
        ('mobiles', 'Mobiles'),
        ('fashion', 'Fashion'),
        ('electronics', 'Electronics'),
        ('Home & Furniture', 'Home & Furniture'),
        ('appliances', 'Appliances'),
        ('sports_books', 'Sports & Books'),
        ('beauty', 'Beauty'),
        ('toys', 'Toys'),
        ('others', 'Others'),
    ]

    product_name = models.CharField(max_length=200)
    category = models.CharField(max_length=100)
    price = models.FloatField()
    desc = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    discount = models.IntegerField(default=0)
    rating = models.IntegerField(default=0.0)

    #new fields
    brand = models.CharField(max_length=100, blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    material = models.CharField(max_length=100, blank=True, null=True)
    dimensions = models.CharField(max_length=100, blank=True, null=True)
    weight = models.CharField(max_length=50, blank=True, null=True)
    warranty = models.CharField(max_length=100, blank=True, null=True)
    model_number = models.CharField(max_length=100, blank=True, null=True)
    special_features = models.TextField(blank=True, null=True)
    included_components = models.TextField(blank=True, null=True)
    care_instructions = models.TextField(blank=True, null=True)
    manufacturer = models.CharField(max_length=100, blank=True, null=True)
    customer_support = models.CharField(max_length=100, blank=True, null=True)
    country_of_origin = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return self.product_name


class Category(models.Model):
    name = models.CharField(max_length=100)

class Order(models.Model):
    items_json = models.TextField()  # store cart data as JSON
    name = models.CharField(max_length=100)
    email = models.EmailField()
    address = models.TextField()
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10)
    phone = models.CharField(max_length=15)
    amount = models.FloatField()
    

    def __str__(self):
        return f"Order {self.id} by {self.name}"


class OrderUpdate(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    update_desc = models.CharField(max_length=500)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.order.id} - {self.update_desc[:20]}..."

