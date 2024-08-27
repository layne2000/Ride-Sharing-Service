from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.db.models import Q
from .forms import RideCreateModelForm, RideOwnerEditModelForm
from django.core.mail import send_mail
import datetime 
from datetime import datetime

from ride.models import Driver, Ride
# Create your views here.

@login_required
def home(request):
    return render(request,"ride/home.html")

def signin(request):
    if request.method == "POST":
        user = authenticate(username=request.POST['username'], password=request.POST['pw'])
        if user is not None:
            login(request, user)
            return redirect('ride:home') # info to be added 
        else:
            messages.error(request, 'Invalid User Information!')
    return render(request, 'ride/signin.html')

def userSignup(request):
    if request.method == "POST":
        pw0 = request.POST['pw0']
        pw1 = request.POST['pw1']
        if pw0 != pw1:
            messages.error(request, "Passwords do not match!" )
            return render(request,'ride/userSignup.html')
        elif User.objects.filter(username = request.POST['username']):
            messages.error(request, "This username has been registered!")
            return render(request,'ride/userSignup.html')
        else:
            user = User.objects.create_user(username=request.POST['username'], email=request.POST['email'], password=request.POST['pw0'])
            user.save()
            messages.success(request, "You successfully create an account!")
            return redirect('ride:signin') 
    else:
        return render(request,'ride/userSignup.html')


@login_required
def userEdit(request, pk):
    if request.method == 'POST':
        if User.objects.filter(username=request.POST['username']) and request.POST['username'] != request.user.username:
            messages.error(request, "This username has been registered!")
            return render(request, 'ride/userEdit.html')
        request.user.username=request.POST['username']
        request.user.email=request.POST['email']
        request.user.save()
        return redirect('ride:userDetail', pk=request.user.id)
    context = {
        'username':request.user.username,
        'email':request.user.email
    }
    return render(request, 'ride/userEdit.html', context) # because user is built-in, we don't need to pass in user object


class DriverCreate(LoginRequiredMixin, CreateView):
    model = Driver
    fields = ['first_name', 'last_name', 'vehicle_type', 'license_plate_number', 'max_num_of_passenger', 'special_vehicle_info']
    def form_valid(self, form):
        form.instance.user = self.request.user # https://stackoverflow.com/questions/10382838/how-to-set-foreignkey-in-createview
        return super(DriverCreate, self).form_valid(form)
    #initial = { user: request.user.pk } #  wrong


class DriverUpdate(LoginRequiredMixin, UpdateView):
    model = Driver
    fields = ['first_name', 'last_name', 'vehicle_type', 'license_plate_number', 'max_num_of_passenger', 'special_vehicle_info']


class DriverDelete(LoginRequiredMixin, DeleteView):
    def form_valid(self, form):
        rides = Ride.objects.filter(driver=self.request.user)
        for ride in rides:
            ride.status = 'open'
            ride.driver = None
            ride.save()
        return super(DriverDelete, self).form_valid(form)
    model = Driver
    success_url = reverse_lazy('ride:home')# can't use reverse here?

class DriverDetailView(LoginRequiredMixin, generic.DetailView):
    model = Driver

@login_required
def driverCheck(request):
    try:
        request.user.driver
    except Driver.DoesNotExist:
        messages.error(request, "You do not have driver account! Please create here." )
        return redirect('ride:driver-create') # can't find the driver-create template if I use render??
    else:
        return redirect('ride:driverDetail', pk=request.user.id)

class UserDetailView(LoginRequiredMixin, generic.DetailView):
    model = User


@login_required
def rideCreate(request):
    if request.method == 'POST':
        # print(request.POST)
        form = RideCreateModelForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['arrival_time']< timezone.now():
                messages.error(request, "You entered a time in the past!")
            elif Ride.objects.filter(owner=request.user, arrival_time=form.cleaned_data['arrival_time']):
                messages.error(request, "You have requested a ride with the same time!")
            else:
                newRide = Ride(address=form.cleaned_data['address'], arrival_time=form.cleaned_data['arrival_time'], \
                passenger_num=form.cleaned_data['passenger_num'],allow_sharer=form.cleaned_data['allow_sharer'],\
                special_request=form.cleaned_data['special_request'], vehicle_type=form.cleaned_data['vehicle_type'], owner=request.user) 
                # newRide.id=newRide.owner.id
                newRide.save()
                messages.success(request, "You successfully request a ride!") # how to filter in the form???
                return redirect('ride:home')
    form = RideCreateModelForm()
    context = {
        'form' : form
    }
    return render(request, 'ride/rideCreate.html', context)
    
# class RideCreate(LoginRequiredMixin, CreateView):
#     model = Ride
#     fields = ['address', 'arrival_time', 'passenger_num', 'allow_sharer', 'special_request','vehicle_type']
#     def form_valid(self, form):
#         form.instance.owner = self.request.user # https://stackoverflow.com/questions/10382838/how-to-set-foreignkey-in-createview
#         form.instance.sharer = None
#         return super(RideCreate, self).form_valid(form)
#     def get_success_url(self):
#         return reverse('ride:home')

class RideUpdate(LoginRequiredMixin, UpdateView):
    model = Ride
    fields = ['address', 'arrival_time', 'passenger_num', 'allow_sharer', 'special_request','vehicle_type']


class RideDelete(LoginRequiredMixin, DeleteView):
    model = Ride
    success_url = reverse_lazy('ride:home')# can't use reverse here?


@login_required
def checkMyOrder(request):
    ownedOpenRides = Ride.objects.filter(owner=request.user) & Ride.objects.filter(status='open')
    ownedConfirmedRides = Ride.objects.filter(owner=request.user) & Ride.objects.filter(status='confirmed')
    # print(ownedRides)
    sharedOpenRides = Ride.objects.filter(status='open') & Ride.objects.filter(sharer__username=request.user.username)# not tested
    # print(sharedOpenRides)
    sharedConfirmedRides = Ride.objects.filter(status='confirmed') & Ride.objects.filter(sharer__username=request.user.username) # not tested
    drivenRides = Ride.objects.filter(driver=request.user) & Ride.objects.filter(status='confirmed')
    context = {
        'ownedOpenRides' : ownedOpenRides,
        'ownedConfirmedRides' : ownedConfirmedRides,
        'sharedOpenRides' : sharedOpenRides,
        'sharedConfirmedRides' : sharedConfirmedRides,
        'drivenRides' : drivenRides
    }
    return render(request, 'ride/myOrders.html', context)


@login_required
def rideDetail(request, pk): # not tested, not sure whether id is usable?
    rides = Ride.objects.filter(id=pk)
    drivers = Driver.objects.filter(user=Ride.objects.get(id=pk).driver) # to make it as a querySet so that we can display it in html
    #print(drivers)
    #print(ride.address)
    context = {
        'rides':rides,
        'drivers':drivers
    }
    return render(request, 'ride/rideDetail.html', context)

@login_required
def markAsComplete(request, pk): # how to make use of rideDetail??
    if request.method == 'POST':
        ride = Ride.objects.get(id=pk) # not sure??
        ride.status = 'complete'
        ride.save()
        messages.success(request, "You successfully mark the ride as complete!")
        return redirect('ride:checkMyOrder')
    # else if it's 'GET'
    rides = Ride.objects.filter(id=pk)
    drivers = Driver.objects.filter(user=Ride.objects.get(id=pk).driver) 
    context = {
        'rides':rides,
        'drivers':drivers
    }
    return render(request, 'ride/markRideAsComplete.html', context)

@login_required
def rideOwnerEditDetail(request, pk):
    if request.method == 'POST':
        ride = Ride.objects.get(id=pk) # not sure??
        # sharers = ride.sharer.all()  
        # if sharers:
        #     for sharer in sharers:
        #         send_mail(
        #         'Ride Sharing Service Notification',
        #         'One of your ride(s) has been canceled by the ride owner, log in ride-sharing-service website to see the details',
        #         'ece568ridesharingservice@outlook.com', 
        #         [sharer.email],
        #         fail_silently=False,
        #         )
        ride.delete()
        messages.info(request, "You cancel the order!") # not sure if info is correct
        return redirect('ride:checkMyOrder')
    # else if it's 'GET'
    rides = Ride.objects.filter(id=pk)
    drivers = Driver.objects.filter(user=Ride.objects.get(id=pk).driver) 
    context = {
        'rides':rides,
        'drivers':drivers
    }
    return render(request, 'ride/rideOwnerEditDetail.html', context)

@login_required
def rideOwnerEditForm(request, pk):
    if request.method == 'POST':
        form = RideCreateModelForm(request.POST)
        if form.is_valid():
            ride = Ride.objects.get(id=pk)
            if form.cleaned_data['arrival_time']< timezone.now():
                messages.error(request, "You entered a time in the past!")
            elif form.cleaned_data['allow_sharer']==False and ride.sharer:
                messages.error(request, "There are sharers joining this ride already. You cannot disable allow_sharer now!")
            else:
                ride.address=form.cleaned_data['address']
                ride.arrival_time=form.cleaned_data['arrival_time']
                ride.passenger_num=form.cleaned_data['passenger_num']
                ride.allow_sharer=form.cleaned_data['allow_sharer']
                ride.special_request=form.cleaned_data['special_request']
                ride.vehicle_type=form.cleaned_data['vehicle_type']
                ride.save()
                messages.success(request, "You successfully modify the ride!") 
                return redirect('ride:checkMyOrder')
    form = RideOwnerEditModelForm()
    context = {
        'form' : form
    }
    return render(request, 'ride/rideOwnerEditForm.html', context)

@login_required
def rideSharerEditDetail(request, pk): # not tested
    if request.method == 'POST':
        ride = Ride.objects.get(id=pk) 
        ride.sharer.remove(request.user) 
        ride.passenger_num -= int(request.POST['num_of_people']) # it can't prevent user from entering wrong answer
        ride.save()
        messages.info(request, "You leave the ride!") 
        return redirect('ride:checkMyOrder')
    # else if it's 'GET'
    rides = Ride.objects.filter(id=pk)
    drivers = Driver.objects.filter(user=Ride.objects.get(id=pk).driver) 
    context = {
        'rides':rides,
        'drivers':drivers
    }
    return render(request, 'ride/rideSharerEditDetail.html', context)


@login_required
def driverRideSearch(request):
    try:
        request.user.driver
    except Driver.DoesNotExist:
        return redirect('ride:driverCheck')
    # attention to the special_request and vehicle_type conditions
    rides = Ride.objects.filter(Q(passenger_num__lte=request.user.driver.max_num_of_passenger) &\
    (Q(special_request='')|Q(special_request=request.user.driver.special_vehicle_info)) & \
    (Q(vehicle_type__isnull=True)|Q(vehicle_type=request.user.driver.vehicle_type)) & Q(status='open'))
    context = {
        'rides':rides
    }
    return render(request, 'ride/driverRideSearch.html', context)


@login_required
def driverRideClaimConfirm(request, pk):
    if request.method == "POST":
        ride = Ride.objects.get(id=pk)
        ride.driver = request.user
        ride.status = 'confirmed'
        ride.save()
        try:
            send_mail(
                'Ride Sharing Service Notification',
                'One of your ride(s) has been confirmed by a driver, log in ride-sharing-service website to see the details',
                'ece568ridesharingservice@outlook.com', 
                [ride.owner.email],
                fail_silently=False,)
            # print("something wrong")
            sharers = ride.sharer.all() # return a querySet
            if sharers:
                for sharer in sharers:
                    send_mail(
                    'Ride Sharing Service Notification',
                    'One of your ride(s) has been confirmed by a driver, log in ride-sharing-service website to see the details',
                    'ece568ridesharingservice@outlook.com', 
                    [sharer.email],
                    fail_silently=False,)
            messages.success(request, "You successfully claim this ride!")
            # print("You successfully claim this ride!")
        except:
            # print("Mistaken email(s) in ride owner or sharer(s)!")
            messages.error(request, "Mistaken email(s) detected in ride owner or sharer(s)! (Order was still confirmed)")
        return redirect('ride:driverRideSearch')
    rides = Ride.objects.filter(id=pk)
    context = {
        'rides':rides
    }
    return render(request, 'ride/driverRideClaimConfirm.html', context)

@login_required
def sharerRideSearch(request):
    if request.method == 'POST':
        # if request.POST['num_of_people'] < 1: # check in the frontend
        #     messages.error(request, "You entered an invalid number of people!")
        earliest_time = datetime.strptime(request.POST['earliest_time'], "%Y-%m-%dT%H:%M")
        latest_time = datetime.strptime(request.POST['latest_time'], "%Y-%m-%dT%H:%M")
        if earliest_time > latest_time:
            messages.error(request, "You entered a lastest arrival time earlier than earliest arrival time!")
        # elif earliest_time < timezone.now(): # not sure 
        #     messages.error(request, "You entered an arrival time window including the past time!")
        else:
            rides = Ride.objects.filter(~Q(owner=request.user) & ~Q(sharer__username=request.user) & \
            Q(address=request.POST['destination']) & Q(arrival_time__range=[request.POST['earliest_time'],\
            request.POST['latest_time']]) & Q(allow_sharer=True) & Q(status='open') ) # not sure 
            print(request.POST['num_of_people'])
            context = {
                'rides':rides, # not sure
                'num_of_people':request.POST['num_of_people']
            }
            return render(request, 'ride/sharerRideSearch.html', context)
    return render(request, 'ride/sharerRideSearchFilter.html')

@login_required
def sharerRideJoin(request, pk, num_of_people): # not sure 
    if request.method == "POST":
        ride = Ride.objects.get(id=pk)
        ride.passenger_num += int(num_of_people) # not sure if int() here is correct
        ride.sharer.add(request.user)
        ride.save()
        messages.success(request, "You successfully join this ride!")
        return redirect('ride:sharerRideSearch')
    rides = Ride.objects.filter(id=pk)
    context = {
        'rides':rides,
        'num_of_people':num_of_people
    }
    return render(request, 'ride/sharerRideJoin.html', context)