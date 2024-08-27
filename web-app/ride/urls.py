from django.urls import path

from . import views

app_name='ride'
urlpatterns = [
    path('',views.home, name='home'),
    path('home/', views.home, name='home'),
    path('signin/', views.signin, name='signin'),
    path('userSignup/', views.userSignup, name='userSignup'),
    path('driver/check/', views.driverCheck, name='driverCheck'),
    path('driver/create/', views.DriverCreate.as_view(), name='driver-create'),
    path('driver/<int:pk>/update/', views.DriverUpdate.as_view(), name='driver-update'),
    path('driver/<int:pk>/delete/', views.DriverDelete.as_view(), name='driver-delete'),
    path('driver/detail/<int:pk>/', views.DriverDetailView.as_view(), name='driverDetail'),
    path('user/detail/<int:pk>/', views.UserDetailView.as_view(template_name= 'ride/user_detail.html'), name='userDetail'),
    path('user/edit/<int:pk>/', views.userEdit, name='userEdit'),
    path('ride/create/', views.rideCreate, name='rideCreate'), # there're two versions I'm testing (1/31 night
    path('ride/detail/<int:pk>', views.rideDetail, name='rideDetail'),
    path('ride/<int:pk>/update/', views.RideUpdate.as_view(), name='ride-update'),
    path('ride/<int:pk>/delete/', views.RideDelete.as_view(), name='ride-delete'),
    path('myorders/',views.checkMyOrder, name='checkMyOrder'),
    path('myorders/<int:pk>/markAsComplete/', views.markAsComplete, name='markAsComplete'),
    path('myorders/<int:pk>/rideOwnerEditDetail/', views.rideOwnerEditDetail, name='rideOwnerEditDetail'),
    path('myorders/<int:pk>/rideOwnerEditForm/', views.rideOwnerEditForm, name='rideOwnerEditForm'),
    path('myorders/<int:pk>/rideSharerEditDetail/', views.rideSharerEditDetail, name='rideSharerEditDetail'),
    path('driverRideSearch/', views.driverRideSearch, name='driverRideSearch'),
    path('driverRideClaimConfirm/<int:pk>/', views.driverRideClaimConfirm, name='driverRideClaimConfirm'),
    path('sharerRideSearch/', views.sharerRideSearch, name='sharerRideSearch'),
    path('sharerRideJoin/<int:pk>/<int:num_of_people>/', views.sharerRideJoin, name='sharerRideJoin'),#
]
