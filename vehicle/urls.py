"""planner URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include

from django.conf import settings # new
from .views import VehicleView, VehicleList, VehicleUpdate, VehicleTypeList, \
    AttendanceView, AttendanceListView

urlpatterns = [
    path('create/', VehicleView.as_view(), name="create-vehicle"),
    path('detail/<int:pk>/', VehicleView.as_view(), name="vehicle-details"),
    path('list/', VehicleList.as_view(), name="vehicle-list"),
    path('update/<int:pk>/', VehicleUpdate.as_view(), name="update-vehicle"),
    path('delete/<int:pk>/', VehicleView().delete, name="vehicle-delete"),
    path('vehicle-type/', VehicleTypeList.as_view(), name="vehicle-types"),
    path('attendance/', AttendanceView.as_view(), name="vehicle-attendance"),
    path('attendance/list/', AttendanceListView.as_view(), name='vehicle-attendance-list')
]
