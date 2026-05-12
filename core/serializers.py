from rest_framework import serializers
from core.models import (
    BlogPost, ClientReview,
    Message,
    PropertySlider,
    Gallary
)
from mainapp.models import(
    ERPProject,
    ERPPlot
    
)


class PropertySliderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertySlider
        fields = '__all__'

class GallarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallary
        fields = '__all__'


# ১. লুপ এড়ানোর জন্য একটি বেসিক প্রজেক্ট সিরিয়ালাইজার
class SimpleERPProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = ERPProject
        fields = '__all__'   # ✅ correct


# ২. প্রপার্টি সিরিয়ালাইজার
class ERPPlotSerializer(serializers.ModelSerializer):
    # ✅ write করার জন্য project id
    project = serializers.PrimaryKeyRelatedField(
        queryset=ERPProject.objects.all()
    )

    # ✅ read করার জন্য nested project
    project_details = SimpleERPProjectSerializer(source='project', read_only=True)

    image = serializers.ImageField(required=False)

    class Meta:
        model = ERPPlot
        fields = '__all__'

# ৩. মেইন প্রজেক্ট সিরিয়ালাইজার
class ERPProjectSerializer(serializers.ModelSerializer):
    cover_image = serializers.ImageField(required=False)
    plots = ERPPlotSerializer(many=True, read_only=True)  # ✅ fixed

    class Meta:
        model = ERPProject
        fields = '__all__'  # ✅ fixed


class FeaturedERPPlotSerializer(serializers.ModelSerializer):
    ERPProject_name = serializers.ReadOnlyField(source='ERPProject.name')
    class Meta:
        model = ERPPlot
        fields = '__all__'


class BlogPostSerializer(serializers.ModelSerializer):
    cover_image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = BlogPost
        fields = '__all__'


class ClientReviewSerializer(serializers.ModelSerializer):
    cover_image = serializers.ImageField(required=False, allow_null=True)
    class Meta:
        model = ClientReview
        fields = '__all__'



class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'