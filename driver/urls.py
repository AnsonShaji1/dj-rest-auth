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
from .views import DriverView, DriverList, DriverUpdate, AttendanceListView, AttendanceView

urlpatterns = [
    path('create/', DriverView.as_view(), name="create-driver"),
    path('detail/<int:pk>/', DriverView.as_view(), name="driver-details"),
    path('list/', DriverList.as_view(), name="driver-list"),
    path('update/<int:pk>/', DriverUpdate.as_view(), name="update-driver"),
    path('delete/<int:pk>/', DriverView().delete, name="driver-delete"),
    path('driver-type/', DriverView().driver_type, name="driver-type"),
    path('attendance/', AttendanceView.as_view(), name="driver-attendance"),
    path('attendance/list/', AttendanceListView.as_view(), name='driver-attendance-list')
]
