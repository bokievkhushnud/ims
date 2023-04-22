from django.db import models
from django.contrib.auth.models import User

# Table for departments
class Department(models.Model):
    name = models.CharField(max_length=100)
    dep_code = models.CharField(max_length=20, default="")
    head = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


# Table of categories
class Category(models.Model):
    name = models.CharField(max_length=100 ,unique=True)
    cat_code = models.CharField(max_length=20, default="")
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    description = models.TextField(blank=True)


    def __str__(self):
        return self.name


# Table for Asset (Single Items)
class Item(models.Model):
    item_type = models.CharField(max_length=20, choices=[("asset", "Asset"), ("accessory", "Accessory"), ("consumable", "Consumable")],
                                 )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    item_name = models.CharField(max_length=300)
    item_code = models.CharField(max_length=100)
    price = models.PositiveIntegerField(default=0)
    currency = models.CharField(max_length=20, default="USD", blank=True)
    quantity = models.PositiveIntegerField(default=1, blank=True)
    quantity_unit = models.CharField(max_length=100, default="PCS")
    min_alert_quantity = models.PositiveIntegerField(default=0)   #-
    location = models.CharField(max_length=100, default="storage", blank=True)
    campus = models.CharField(max_length=20, choices=[(
        "NAR", "Naryn"), ("KHG", "Khorog"), ("TKL", "Tekeli")], default="Naryn")
    description = models.TextField(blank=True)
    vendor = models.CharField(max_length=100, blank=True)
    date_received = models.DateField()
    expiration_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True)
    order_number = models.CharField(max_length=100, blank=True)
    holder = models.ManyToManyField(User, blank=True,  related_name="holder")  # not visible
    qr_code = models.CharField(
        max_length=200, blank=True, default="")  # not visible
    image = models.ImageField(default='items/default.png', upload_to='items')  # +
    status = models.CharField(  # not visible
        max_length=20, choices=[("available", "Available"), ("outinuse", "Out In Use"), ("broken", "Broken")],
        default="available"
    )

    def __str__(self):
        return self.item_name


# Table for Licenses
class License(models.Model):
    license_id = models.CharField(max_length=20, )
    license_name = models.CharField(max_length=100, default="")
    purchase_cost = models.PositiveIntegerField(default=0)
    notification_days = models.PositiveIntegerField(default=3)
    licensed_to = models.CharField(max_length=100, default="")
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    product_key = models.TextField(blank=True)
    licensed_by = models.CharField(max_length=100, blank=True)
    purchased_date = models.DateField(null=True)
    expiration_date = models.DateField(blank=True, null=True)
    order_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.license_name


# Table for Items that are out in use
class ItemAssignment(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="item", blank=True)
    quantity = models.PositiveIntegerField(default=1)
    action = models.CharField(max_length=20, choices=[("assign", "assign"), ("return", "return")])
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    location = models.CharField(max_length=100)
    requestor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="requestor")
    done_by = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True)
    due_date = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=3, choices=[('in', 'in'), ('out','out')], default='in')

    def __str__(self):
        return f"{self.requestor.username}-{self.item.item_name}"


# Table to store item history
class ItemHistory(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    transaction = models.ForeignKey(ItemAssignment, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.item.item_name} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"


# model for user profiles
class Profile(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(default='items/default.png', upload_to='profile_pics')
    
    def __str__(self):
        return f"{self.owner.first_name}-{self.owner.last_name}"

