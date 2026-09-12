from django.db import models


class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=200, blank=True)
    phone_number = models.CharField(max_length=32, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    stripe_customer_id = models.CharField(max_length=64, blank=True)
    marketing_opt_in = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
