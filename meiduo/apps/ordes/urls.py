from django.urls import path
from apps.ordes.views import *

urlpatterns = [
    path('orders/settlement/', OrderView.as_view()),
]
