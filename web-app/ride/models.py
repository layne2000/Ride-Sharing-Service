from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

# Create your models here.
VEHICLE_TYPE_CHOICES = [
        ('Sedan', 'Sedan'),# what's difference of the first and second parameter?
        ('SUV', 'SUV'),
        ('Hatchback', 'Hatchback'),
        ('Pickup', 'Pickup'),
        ('Van', 'Van'),
        ('Coupe', 'Coupe'),
        ('Luxury', 'Luxury'),
    ]

class Ride(models.Model):
    STATUS_CHOICES = [
        ('open','open'),
        ('confirmed','confirmed'),
        ('complete','complete'),
    ]
    owner = models.ForeignKey(User, related_name='owner', on_delete=models.CASCADE)
    sharer = models.ManyToManyField(User, related_name='sharers', blank=True)  # why there's a default setting which includes all the existing users?
    driver = models.ForeignKey(User, related_name='rideDriver',on_delete=models.CASCADE, blank=True, null=True) 
    address = models.CharField(max_length=100)
    arrival_time = models.DateTimeField(help_text='Format: 2023-03-01 12:00')
    passenger_num = models.PositiveIntegerField(default=1)
    allow_sharer =  models.BooleanField(default=False, null=False)
    special_request = models.CharField(max_length=300, blank=True) # blank and null ?? I can't add null=True??
    vehicle_type = models.CharField(choices=VEHICLE_TYPE_CHOICES, blank=True, null=True, max_length=10)
    status = models.CharField(choices=STATUS_CHOICES, max_length=10, default='open')
    class Meta:
        ordering = ['arrival_time']
    def get_absolute_url(self):
        return reverse('ride:rideDetail', args=[str(self.id)])
    def __str__(self):
        return f'Ride owned by {self.owner.username}'

class Driver(models.Model):
    user = models.OneToOneField(User, related_name='driver', on_delete=models.CASCADE, primary_key=True) # primary key here becomes user or user.id?
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    vehicle_type = models.CharField(choices=VEHICLE_TYPE_CHOICES, max_length=10)
    license_plate_number = models.CharField(max_length=10)
    max_num_of_passenger = models.PositiveIntegerField()
    special_vehicle_info = models.CharField(max_length=300, blank=True)
    def get_absolute_url(self):
        return reverse('ride:driverDetail', args=[str(self.user.id)])
    def __str__(self):
        return f'{self.first_name}, {self.last_name}'

