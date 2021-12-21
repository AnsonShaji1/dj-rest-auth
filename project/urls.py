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
from .views import ProjectView, ProjectList, ProjectUpdate

urlpatterns = [
    path('create/', ProjectView.as_view(), name="create-project"),
    path('detail/<int:project_id>/', ProjectView.as_view(), name="project-details"),
    # path('update/<int:pk>/', update, name="edit-project"),
    path('list/', ProjectList.as_view(), name="project-list"),
    path('update/<int:pk>/', ProjectUpdate.as_view(), name="update-project"),
    path('delete/<int:project_id>/', ProjectView().delete, name="project-delete")
]
