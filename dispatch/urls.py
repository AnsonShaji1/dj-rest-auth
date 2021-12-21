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
from .views import DispatchView, DispatchList, DispatchTimeCheck, \
    TimePlotView, DispatchStackView, UpdateStackStatus, DelayedReasonView, \
    UpdateRemarkView, ActiveCheckView, DispatchFilterView

urlpatterns = [
    path('create-or-update/', DispatchView.as_view(), name="create-or-update-dispatch"),
    path('detail/<int:pk>/', DispatchView.as_view(), name="dispatch-details"),
    path('list/', DispatchList.as_view(), name="dispatch-list"),
    path('delete/<int:pk>/', DispatchView().delete, name="dispatch-delete"),
    path('related-data/', DispatchView().relatedData, name="related-data"),
    path('time-check/', DispatchTimeCheck.as_view(), name='time-check' ),
    path('time-plot/', TimePlotView.as_view(), name="time-plot"),
    path('stack-list/', DispatchStackView.as_view(), name="stack_list"),
    path('stack-status/', DispatchStackView().get_stack_status, name='status_list'),
    path('update-dis-status/', UpdateStackStatus.as_view(), name='update_dis_status'),
    path('delayed-reasons/', DelayedReasonView.as_view(), name="delayed-reason"),
    path('update-remark/', UpdateRemarkView.as_view(), name="update-remark"),
    path('stack-filter-data/', DispatchView().stackfilterData, name="related-data"),
    path('driver-vehicle-datecheck/', ActiveCheckView.as_view(), name="active-check"),
    path('filter/', DispatchFilterView.as_view(), name="dispatch-filter"),
    path('filter-related-data/', DispatchFilterView().relatedData, name="filter-related-data")
]
