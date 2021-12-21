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
from .views import DashboardView, VehicleUtilizationView, DriverUtilizationView, DashboardDeliveryView

urlpatterns = [
    # path('/', DispatchView.as_view(), name="create-or-update-dispatch")
    path('fetch-all/', DashboardView.as_view(), name="fetch-all"),
    path('vehicle-utilization/', VehicleUtilizationView.as_view(), name="vehicle-utilization"),
    path('driver-utilization/', DriverUtilizationView.as_view(), name="driver-utilization"),
    path('dashboard-delivery/', DashboardDeliveryView.as_view(), name="dashboard-delivery"),
]
