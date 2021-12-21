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
from .views import StackView, StackList, StackUpdate

urlpatterns = [
    path('create/', StackView.as_view(), name="create-stack"),
    path('detail/<int:pk>/', StackView.as_view(), name="stack-details"),
    path('list/', StackList.as_view(), name="stack-list"),
    path('update/<int:pk>/', StackUpdate.as_view(), name="update-stack"),
    path('delete/<int:pk>/', StackView().delete, name="stack-delete"),
    path('stack-type/', StackView().stack_type, name="stack-types")
]
