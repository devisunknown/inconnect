from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import status, generics, permissions
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Interest, Profile, Chat, ChatMember
from .serializers import (
    SignupSerializer,
    LoginSerializer,
    UserSerializer,
    InterestSerializer,
    InterestSelectionSerializer,
    MatchSerializer,
)


class SignupView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data,
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password'],
        )
        if user is None:
            return Response(
                {'error': 'Invalid credentials.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data,
        })


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class InterestListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = Interest.objects.all()
    serializer_class = InterestSerializer


class InterestSelectionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = InterestSelectionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        interest_ids = serializer.validated_data['interest_ids']
        interests = Interest.objects.filter(id__in=interest_ids)
        profile, _ = Profile.objects.get_or_create(user=request.user)
        profile.interests.set(interests)
        return Response({
            'interests': InterestSerializer(interests, many=True).data,
        })


class MatchesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        my_interest_ids = set(profile.interests.values_list('id', flat=True))

        existing_chats = {}
        for m in request.user.chats.filter(is_group=False).prefetch_related('participants').exclude(participants=request.user):
            other = m.other_user(request.user)
            if other:
                existing_chats[other.id] = m.id

        matches_list = []
        other_profiles = Profile.objects.exclude(user=request.user).prefetch_related('interests', 'user')
        for p in other_profiles:
            p_interest_ids = set(i.id for i in p.interests.all())
            if not my_interest_ids or not p_interest_ids:
                continue
            shared_ids = my_interest_ids & p_interest_ids
            score = round(len(shared_ids) / len(my_interest_ids | p_interest_ids) * 100)
            if score > 0:
                shared = [i for i in p.interests.all() if i.id in shared_ids]
                matches_list.append({
                    'user_id': p.user_id,
                    'username': p.user.username,
                    'full_name': p.full_name,
                    'bio': p.bio,
                    'profile': p,
                    'score': score,
                    'shared_interests': shared,
                    'existing_chat_id': existing_chats.get(p.user_id),
                })
        matches_list.sort(key=lambda m: m['score'], reverse=True)

        serializer = MatchSerializer(matches_list, many=True)
        return Response(serializer.data)
