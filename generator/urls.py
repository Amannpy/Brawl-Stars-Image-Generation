from django.urls import path
from . import views

urlpatterns = [
    path('generate/',views.GenerateImageView.as_view(), name='generate-image'),
]

