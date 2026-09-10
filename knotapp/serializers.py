from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import Interest, Profile


class InterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = ['id', 'name', 'icon', 'category']


class ProfileSerializer(serializers.ModelSerializer):
    interests = InterestSerializer(many=True, read_only=True)
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = Profile
        fields = [
            'id', 'bio', 'interests', 'avatar', 'location',
            'hobbies', 'personality', 'email_verified', 'full_name',
            'created_at',
        ]


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile']
        read_only_fields = ['id']


class SignupSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=150)
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password1 = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Username already taken.')
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already registered.')
        return value

    def validate(self, attrs):
        if attrs['password1'] != attrs['password2']:
            raise serializers.ValidationError({'password2': 'Passwords do not match.'})
        validate_password(attrs['password1'])
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password1'],
            first_name=validated_data['first_name'],
        )
        Profile.objects.create(user=user)
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class InterestSelectionSerializer(serializers.Serializer):
    interest_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1,
    )

    def validate_interest_ids(self, value):
        existing = Interest.objects.filter(id__in=value).count()
        if existing != len(value):
            raise serializers.ValidationError('One or more interest IDs are invalid.')
        return value


class MatchSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    username = serializers.CharField()
    full_name = serializers.CharField()
    bio = serializers.CharField(allow_blank=True)
    avatar = serializers.SerializerMethodField()
    shared_interests = InterestSerializer(many=True)
    score = serializers.IntegerField()
    existing_chat_id = serializers.IntegerField(allow_null=True)

    def get_avatar(self, obj):
        profile = obj.get('profile')
        if profile and profile.avatar:
            return profile.avatar.url
        return None
