from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserSerializer
from .models import User,Plant
import pickle
from rest_framework import status
import joblib
from rest_framework.exceptions import APIException, AuthenticationFailed
from .authentication import create_access_token, create_refresh_token, decode_access_token, decode_refresh_token
import jwt,datetime
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
with open('C:/Users/Utilisateur/Desktop/iset/2eme/semestre1/projet dcp/app/back-end/auth/modele/recommendation_modele.pkl', 'rb') as file:
     modele = pickle.load(file)
#modele = joblib.load('./modele/RF_model.joblib')
# Create your views here.
class RegisterView(APIView):
    def post(self,request):
        serializer=UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            'user_id': user.id,  # Renvoyer l'ID de l'utilisateur créé
            'message': 'Utilisateur enregistré avec succès.'
        })
@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    def post(self, request):
        email = request.data['email']
        password = request.data['password']

        # Recherche de l'utilisateur par email
        user = User.objects.filter(email=email).first()
      
        if user is None:
            raise AuthenticationFailed('Utilisateur introuvable!')
        if not user.check_password(password):
            raise AuthenticationFailed('Mot de passe incorrect!')

        # Création du payload pour le jeton JWT
        payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow()
        }
        
        # Génération du jeton JWT
        token = jwt.encode(payload, 'secret', algorithm='HS256')
        response = Response()

        # Envoi du jeton JWT dans les cookies
        response.set_cookie(key='jwt', value=token, httponly=True)

        # Ajout de l'ID de l'utilisateur dans la réponse
        response.data = {
            'jwt': token,
            'user_id': user.id  # Ajout de l'ID de l'utilisateur
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
    def post(self, request):
        try:
            data = request.data
            user_id = data.get('user_id')  # Récupérer l'ID utilisateur
            
            # Vérifiez si l'utilisateur existe
            user = User.objects.get(id=user_id)

            # Préparer les données pour le modèle
            entree_modele = [data['N'], data['P'], data['K'], data['temp'], data['humidity'], data['ph'], data['rain']]
            resultat = modele.predict([entree_modele])

            # Enregistrer la recommandation dans la base de données
            user.recommendation = resultat[0]
            user.save()

            return Response({'resultat': resultat[0]}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'Utilisateur non trouvé'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
class RecommendationDetailView(APIView):
     def get(self,request):
          try:
               user_id=request.query_params.get('user_id')
               if not user_id:
                    return Response({'error':'ID utilisateur manquant.'},status=status.HTTP_400_BAD_REQUEST)
               user=User.objects.get(id=user_id)
               recommendation=user.recommendation
               if not recommendation:
                    return Response({'error':'Aucune recommendation trouvée pour cet utilisateur.'},status=status.HTTP_404_NOT_FOUND)
               plant = Plant.objects.get(name=recommendation)
               return Response({
                'name': plant.name,
                'description': plant.description,
                'image':plant.image,
                
               }, status=status.HTTP_200_OK)
          except User.DoesNotExist:
            return Response({'error': 'Utilisateur non trouvé.'}, status=status.HTTP_404_NOT_FOUND)
          except Plant.DoesNotExist:
            return Response({'error': f'Plante "{recommendation}" non trouvée.'}, status=status.HTTP_404_NOT_FOUND)
          except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)