from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserSerializer
from .models import User
import pickle
from rest_framework import status
import joblib
from rest_framework.exceptions import APIException, AuthenticationFailed
from .authentication import create_access_token, create_refresh_token, decode_access_token, decode_refresh_token
import jwt,datetime
with open('./modele/recommendation_modele.pkl', 'rb') as file:
     modele = pickle.load(file)
#modele = joblib.load('./modele/RF_model.joblib')
# Create your views here.
class RegisterView(APIView):
    def post(self,request):
        serializer=UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    

class LoginView(APIView):
    def post(self,request):
        email=request.data['email']
        password=request.data['password']
        user=User.objects.filter(email=email).first()
      
        if user is None:
             raise AuthenticationFailed('user not found!')
        if not user.check_password(password):
             raise AuthenticationFailed('Incorrect password!')
        payload={
             'id':user.id,
             'exp':datetime.datetime.utcnow()+datetime.timedelta(minutes=60),
             'iat':datetime.datetime.utcnow()
         }
        
        token=jwt.encode(payload,'secret',algorithm='HS256')
        response=Response()
        response.set_cookie(key='jwt',value=token,httponly=True)
        response.data={
             'jwt':token
         }
        return response
class UserView(APIView):
        def get(self,request):
            token=request.COOKIES.get('jwt')

            if not token :
                 raise AuthenticationFailed('Unauthenticated!')
            
            try:
                 payload=jwt.decode(token,'secret',algorithms=['HS256'])
            except jwt.ExpiredSignatureError:
                 raise AuthenticationFailed('Unauthenticated!')
            
            user=User.objects.filter(id=payload['id']).first()
            serializer=UserSerializer(user)
            return Response(serializer.data)
class LogoutView(APIView):
     def post(self,request):
          response=Response()
          response.delete_cookie('jwt')
          response.data={
               "message":"success!"
          }
          return response

class Prediction_View(APIView):
    def prediction_view(request):
      try:
      
        data = request.data  # Récupérer les données JSON envoyées
        # Extraire les données nécessaires
        entree_modele = [data['N'], data['K'], ...]
        # Obtenir la prédiction
        resultat = modele.predict([entree_modele])
        # Retourner la prédiction en JSON
        return Response({'resultat': resultat[0]}, status=status.HTTP_200_OK)
      except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
  