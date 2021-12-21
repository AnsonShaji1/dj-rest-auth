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
from .views import *

urlpatterns = [
    path('user-list/', AccountsView.as_view(), name="user-list"),
    path('role-type/', RoleTypeView.as_view(), name="role-type"),
    path('update/', AccountsView.as_view(), name="update-user"),
    path('delete/<int:pk>/', AccountsView().delete, name="user-delete"),
    path('settings/', SettingsView.as_view(), name="settings"),
    # path('setting/user-role/', UserRoleView.as_view(), name="user-role"),
    # path('setting/stack-status/', StackStatusView.as_view(), name="stack-status"),
    # path('setting/driver-type/', DriverTypeView.as_view(), name="driver-type"),
    # path('setting/stack-type/', StackTypeView.as_view(), name="stack-type"),
    # path('setting/vehicle-type/', VehicleTypeView.as_view(), name="vehicle-type"),
    path('settings/common/', CommonSettingView.as_view(), name="common-settings")
]
