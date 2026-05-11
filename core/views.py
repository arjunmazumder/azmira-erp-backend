from rest_framework import viewsets, filters, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from core.response import success_response, error_response
from core.models import (
    ClientReview,
    Message,
    BlogPost
    
)
from mainapp.models import(
    ERPProject, ERPPlot,
)

from core.serializers import(
    ERPProjectSerializer, ERPPlotSerializer, FeaturedERPPlotSerializer,
    BlogPostSerializer, ClientReviewSerializer,MessageSerializer
) 
from core.filters import (
    ERPPlotFilter,
    ERPProjectFilter
)

# views.py

from rest_framework import generics
from .models import PropertySlider
from .serializers import PropertySliderSerializer


# CREATE + LIST
class PropertySliderListCreateView(generics.ListCreateAPIView):
    queryset = PropertySlider.objects.all().order_by('-id')
    serializer_class = PropertySliderSerializer


# RETRIEVE + UPDATE + DELETE
class PropertySliderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PropertySlider.objects.all()
    serializer_class = PropertySliderSerializer

   
# ২. টাইপ অনুযায়ী প্রজেক্ট পাওয়ার জন্য আলাদা ভিউ
class ERPProjectByTypeView(APIView):
    def get(self, request):
        ERPProject_type = request.query_params.get('ERPProject_type')

        if ERPProject_type:
            ERPProjects = ERPProject.objects.filter(ERPProject_type=ERPProject_type)
        else:
            ERPProjects = ERPProject.objects.all()

        serializer = ERPProjectSerializer(ERPProjects, many=True)
        return success_response("ERPProjects fetched", serializer.data)

# Name base search

class ERPProjectSearchByNameView(APIView):
    def get(self, request):
        # query param থেকে ERPProject_name নেওয়া
        ERPProject_name = request.query_params.get('ERPProject_name', '').strip()

        # নামের আংশিক মিল চেক
        if ERPProject_name:
            ERPProjects = ERPProject.objects.filter(name__icontains=ERPProject_name).order_by('-created_at')
        else:
            ERPProjects = ERPProject.objects.all().order_by('-created_at')

        if ERPProjects.exists():
            serializer = ERPProjectSerializer(ERPProjects, many=True)
            return  success_response("successful !!", serializer.data)

        return success_response("No ERPProjects found", serializer.data)

class ERPProjectByLocationView(APIView):
    def get(self, request):
        location_param = request.query_params.get('location', '')
        location_text = location_param.replace('-', ' ')

        ERPProjects = ERPProject.objects.filter(location__icontains=location_text)
        total_count = ERPProjects.count()

        serializer = ERPProjectSerializer(ERPProjects, many=True)

        return success_response(
            "ERPProjects by location",
            {
                "count": total_count,
                "results": serializer.data
            }
        )

   
class FeaturedERPPlotListView(APIView):
    def get(self, request):
        featured_properties = ERPPlot.objects.filter(is_featured=True).order_by('-created_at')
        serializer = FeaturedERPPlotSerializer(featured_properties, many=True)
        return success_response("Featured properties retrieved successfully", serializer.data)
    


class LatestBlogPostView(APIView):
    # GET: Fetch all blog posts (Latest first)
    def get(self, request):
        # We order by -created_at to get the "Latest" posts first
        blog_posts = BlogPost.objects.all().order_by('-created_at')
        serializer = BlogPostSerializer(blog_posts, many=True)
        
        # Using your custom success_response utility
        return success_response(
            "Blog posts retrieved successfully",
            serializer.data,
            status_code=status.HTTP_200_OK
        )

    # POST: Create a blog post
    def post(self, request):
        serializer = BlogPostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return success_response(
                "Blog post created successfully",
                serializer.data,
                status_code=status.HTTP_201_CREATED
            )
        return error_response("Failed to create blog post", serializer.errors)
    

class ClientReviewCreateView(APIView):
    # permission_classes = [IsAdminUser]  # Only admin can post reviews

    def post(self, request):
        serializer = ClientReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return success_response("Client review created successfully", serializer.data, status_code=status.HTTP_201_CREATED)
        return error_response("Failed to create review", serializer.errors)

class ClientReviewListView(APIView):
    # Anyone can view published reviews
    def get(self, request):
        reviews = ClientReview.objects.filter(is_published=True).order_by('-created_at')
        serializer = ClientReviewSerializer(reviews, many=True)
        return success_response("Client reviews retrieved successfully", serializer.data)
    
class MessageCreateView(APIView):
    def post(self, request):
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return success_response(
                "Message sent successfully",
                serializer.data,
                status_code=status.HTTP_201_CREATED
            )
        return error_response("Failed to send message", serializer.errors)
    
# GET: admin-only endpoint to view all messages
class MessageListAdminView(APIView):
    # permission_classes = [IsAdminUser]

    def get(self, request):
        messages = Message.objects.all().order_by('-created_at')
        serializer = MessageSerializer(messages, many=True)
        return success_response("All messages retrieved successfully", serializer.data)
    



#-----------------ERPProject searching----------------

class ERPProjectViewSet(viewsets.ModelViewSet):
    # permission_classes = [IsAuthenticated]

    # ✅ Correct related_name = 'plots'
    queryset = ERPProject.objects.all().prefetch_related('plots').order_by('-created_at')

    serializer_class = ERPProjectSerializer

    # ✅ Filter + Search + Ordering
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    # ✅ Custom filter class
    filterset_class = ERPProjectFilter

    # ✅ Correct search fields (model অনুযায়ী)
    search_fields = [
        'project_name',
        'project_code',
        'city',
        'district',
        'upazila',
        'plots__plot_number',   # related field search
    ]

    # ✅ Ordering fields
    ordering_fields = ['created_at', 'total_project_value', 'total_land_area']
    ordering = ['-created_at']


    # 🔹 List
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return success_response(
            f"Successfully retrieved {queryset.count()} ERPProjects",
            serializer.data
        )


    # 🔹 Retrieve
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response("ERPProject details retrieved successfully", serializer.data)


    # 🔹 Create
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return success_response(
                "ERPProject created successfully",
                serializer.data,
                status_code=status.HTTP_201_CREATED
            )
        return error_response("ERPProject creation failed", serializer.errors)


    # 🔹 Update
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return success_response("ERPProject updated successfully", serializer.data)

        return error_response("ERPProject update failed", serializer.errors)


    # 🔹 Partial Update
    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


    # 🔹 Delete
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return success_response(
            "ERPProject deleted successfully",
            None,
            status_code=status.HTTP_204_NO_CONTENT
        )   

#-----------------ERPPlot searching-----------------------
class ERPPlotViewSet(viewsets.ModelViewSet):
    # permission_classes = [IsAuthenticated]

    queryset = ERPPlot.objects.all().select_related('project').order_by('-created_at')
    serializer_class = ERPPlotSerializer

    # ✅ Filter + Search + Ordering
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    # ❗ Option 1 (Recommended): direct fields (no FilterSet error)
    filterset_fields = [
        'project',
        'plot_type',
        'status',
        'facing',
        'area_unit',
        'bedrooms',
        'bathrooms',
    ]

    # ✅ Search ক্ষেত্র
    search_fields = [
        'plot_number',
        'flat_number',
        'project__project_name',
        'project__city',
    ]

    # ✅ Ordering
    ordering_fields = [
        'created_at',
        'total_price',
        'final_price',
        'area',
        'floor_number',
    ]
    ordering = ['-created_at']


    # 🔹 List
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        return success_response(
            "Plots retrieved successfully",
            {
                "count": queryset.count(),
                "results": serializer.data
            }
        )


    # 🔹 Retrieve
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response("Plot details retrieved", serializer.data)


    # 🔹 Create
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return success_response(
                "Plot created successfully",
                serializer.data,
                status_code=status.HTTP_201_CREATED
            )
        return error_response("Plot creation failed", serializer.errors)


    # 🔹 Update
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return success_response("Plot updated successfully", serializer.data)

        return error_response("Plot update failed", serializer.errors)


    # 🔹 Partial Update
    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


    # 🔹 Delete
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return success_response(
            "Plot deleted successfully",
            None,
            status_code=status.HTTP_204_NO_CONTENT
        )