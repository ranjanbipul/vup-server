from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.contrib.auth.hashers import check_password, make_password
from home.models import Video, Comment
import sys

User = get_user_model()


class ValidatedModelSerializer(serializers.ModelSerializer):
    """ This class add model validation to Model Serializer """

    def validate(self, attrs):
        self.Meta.model(**attrs).clean()
        return attrs

    def validate_user(self, value):
        """ Will insert current authenticated user """
        return self.context["request"].user


class NewUserSerializer(serializers.ModelSerializer):
    re_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'username', 'password', 're_password',)
        extra_kwargs = {'password': {'write_only': True}}

    def validate_email(self, value):
        try:
            User.objects.get(email=value)
            raise serializers.ValidationError("Email already registered.")
        except User.DoesNotExist:
            return value
        except User.MultipleObjectsReturned:
            raise serializers.ValidationError("Email used many times. Contact support if necessary.")


    def validate_password(self, value):
        if len(value) < 6:
            raise serializers.ValidationError("Password must be at least 6 character long")
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["re_password"]:
            raise serializers.ValidationError("Password do not match")
        attrs.pop('re_password', None)
        self.Meta.model(**attrs).clean()
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.password = make_password(password)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            if attr == 'password':
                instance.password = make_password(password)
            else:
                setattr(instance, attr, value)
        instance.save()
        return instance

# Authenticated serializers

class UserNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username')

class CommentSerializer(ValidatedModelSerializer):
    user = serializers.SlugRelatedField(required=False, allow_null=True, default=None, read_only=True,
                                        slug_field='username')
    class Meta:
        model = Comment
        fields = '__all__'
#
# class CommentViewSerializer(serializers.ModelSerializer):
#     user = UserNameSerializer(many=False,read_only=True)
#     class Meta:
#         model = Comment
#         fields = '__all__'

class VideoSerializer(ValidatedModelSerializer):
    user = serializers.SlugRelatedField(required=False, allow_null=True, default=None, read_only=True,
                                        slug_field='username')
    class Meta:
        model = Video
        fields = '__all__'
        read_only_fields = ['image']

# class VideoViewSerializer(serializers.ModelSerializer):
#     user = UserNameSerializer(many=False,read_only=True)
#     comment_set = CommentViewSerializer(many=True,read_only=True)
#     class Meta:
#         model = Video
#         fields = ('id','file','user','title','image','description','created_at','updated_at','comment_set')
