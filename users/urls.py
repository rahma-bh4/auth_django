
from django.urls import path
from .views import RegisterView,LoginView,UserView,LogoutView,Prediction_View,RecommendationDetailView
urlpatterns = [
    
    path('register',RegisterView.as_view()),
    path('login',LoginView.as_view()),
    path('user',UserView.as_view()),
    path('logout',LogoutView.as_view()),
    path('recommendation',Prediction_View.as_view()),
    path('recommendation-detail', RecommendationDetailView.as_view()),
]
