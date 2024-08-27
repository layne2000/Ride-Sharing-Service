import datetime
from django import forms
from django.forms import ModelForm
from .models import Ride
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User

class RideCreateModelForm(ModelForm):
    # def clean_arrival_time(self):
    #     arrivalTime = self.cleaned_data['arrival_time']
    #     if arrivalTime < timezone.now(): # tested
    #         raise ValidationError("You entered a time in the past!") # not the same as tutorial
    #     #if Ride.objects.filter(owner=user, arrival_time=arrivalTime):# how to filter in this case??
    #     #    raise ValidationError("You have requested a ride with the same time!")
    #     return arrivalTime
    class Meta:
        model = Ride
        fields = ['address', 'arrival_time', 'passenger_num', 'allow_sharer', 'special_request','vehicle_type']

class RideOwnerEditModelForm(ModelForm):
    # validation functions to be added....................
    class Meta:
        model = Ride
        fields = ['address', 'arrival_time', 'passenger_num', 'allow_sharer', 'special_request','vehicle_type']