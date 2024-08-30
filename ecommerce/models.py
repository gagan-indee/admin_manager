from django.db import models

# Create your models here.

class Customer(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    mobile = models.CharField(max_length=10, unique=True)
    email = models.EmailField(unique=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Address(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='addresses')
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=10)
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True)
    landmark = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=6)
    disabled_on = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.name}, {self.address_line_1}, {self.pincode}"


class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


class Order(models.Model):
    STATUS_CHOICES = [("active", "active"), ("completed", "completed"), ("canceled", "canceled")]
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    address = models.ForeignKey(Address, on_delete=models.CASCADE, related_name='orders')
    products = models.ManyToManyField(Product, through='OrderItem', related_name='orders')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    order_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="active")
    created_on = models.DateTimeField(auto_now_add=True)

    def calculate_total_amount(self):
        total = self.order_items.aggregate(total_amount=models.Sum('total_item_price'))['total_amount'] or 0
        return total

    def save(self, *args, **kwargs):
        if self.pk is None:
            super().save(*args, **kwargs)
        self.total_amount = self.calculate_total_amount()
        super().save()

    def __str__(self):
        return f"Order {self.id} for {self.customer}"
    

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    total_item_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_on = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.pk is None:
            super().save(*args, **kwargs)
        self.total_item_price = self.product.price * self.quantity
        super().save(update_fields=['total_item_price'])
        self.order.total_amount = self.order.calculate_total_amount()
        self.order.save(update_fields=['total_amount'])

    def __str__(self):
        return f"{self.product} x {self.quantity} in Order {self.order.id}"