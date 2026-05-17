# from rest_framework import generics, status
# from rest_framework.response import Response
# from rest_framework.views import APIView
# from rest_framework.permissions import IsAuthenticated, AllowAny
# from rest_framework_simplejwt.views import TokenObtainPairView

# from users.serializers import RegisterSerializer, UserSerializer
# from users.models import User


# # ✅ Register
# class RegisterView(generics.CreateAPIView):
#     serializer_class = RegisterSerializer
#     permission_classes = [AllowAny]

#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         if serializer.is_valid():
#             user = serializer.save()
#             return Response({
#                 "message": "Registration successful",
#                 "data": {
#                     "requests": [UserSerializer(user).data]
#                 }
#             }, status=status.HTTP_201_CREATED)

#         return Response({
#             "message": "Registration failed",
#             "data": {"requests": [serializer.errors]}
#         }, status=status.HTTP_400_BAD_REQUEST)


# # ✅ Login (JWT)
# class CustomLoginView(TokenObtainPairView):
#     def post(self, request, *args, **kwargs):
#         # 1. Instantiate the default JWT serializer to validate email/password
#         serializer = self.get_serializer(data=request.data)

#         try:
#             # 2. Check credentials
#             serializer.is_valid(raise_exception=True)
#         except Exception:
#             return Response({
#                 "message": "Login failed",
#                 "data": {"errors": serializer.errors}
#             }, status=status.HTTP_400_BAD_REQUEST)

#         # 3. SimpleJWT attaches the user object to the serializer upon success
#         user = serializer.user
#         token_data = serializer.validated_data
        
#         # 4. Use your custom UserSerializer for the response data
#         user_data = UserSerializer(user).data

#         # 5. Return tokens first, then user info
#         return Response({
#             "message": "Login successful",
#             "data": {
#                 "tokens": {
#                     "access": token_data.get('access'),
#                     "refresh": token_data.get('refresh')
#                 },
#                 "userinfo": user_data
#             }
#         }, status=status.HTTP_200_OK)

# # ✅ Profile View (GET + UPDATE)
# class UserProfileView(APIView):
#     permission_classes = [IsAuthenticated]
    
#     # Get Profile
#     def get(self, request):
#         serializer = UserSerializer(request.user)
#         return Response({
#             "message": "Profile fetched successfully",
#             "data": {
#                 "requests": [serializer.data]
#             }
#         }, status=status.HTTP_200_OK)

#     # Update Profile
#     def put(self, request):
#         serializer = UserSerializer(request.user, data=request.data, partial=True)

#         if serializer.is_valid():
#             serializer.save()
#             return Response({
#                 "message": "Profile updated successfully",
#                 "data": {
#                     "requests": [serializer.data]
#                 }
#             }, status=status.HTTP_200_OK)

#         return Response({
#             "message": "Profile update failed",
#             "data": {"requests": [serializer.errors]}
#         }, status=status.HTTP_400_BAD_REQUEST)