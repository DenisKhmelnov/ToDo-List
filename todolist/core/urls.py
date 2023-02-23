from django.urls import path
from todolist.core.views import SignUpView

urlpatterns = [
    path('signup', SignUpView.as_view(), name='signup'),
]