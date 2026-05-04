from django.db import models

# Create your models here.
from django.db import models
from django.utils import timezone
# from cloudinary.models import CloudinaryField

# class Project(models.Model):
#     PROJECT_TYPE_CHOICES = [
#         ('residential', 'Residential'),
#         ('commercial', 'Commercial'),
#         ('mixed', 'Mixed Use'),
#     ]
    
#     # Building Type Choice
#     BUILDING_TYPE_CHOICES = [
#         ('single_building', 'Single Building'),
#         ('multi_building_complex', 'Multi Building Complex'),
#         ('skyscraper', 'Skyscraper'),
#     ]

#     STATUS_CHOICES = [
#         ('upcoming', 'Upcoming'),
#         ('under_construction', 'Under Construction'),
#         ('ready', 'Ready to Move'),
#     ]

#     # Basic Info
#     name = models.CharField(max_length=255, verbose_name="Project Name")
#     developer_name = models.CharField(max_length=255, blank=True, null=True)
#     location = models.TextField()
#     project_type = models.CharField(max_length=20, choices=PROJECT_TYPE_CHOICES, default='residential')
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    
#     # New Required Fields
#     building_type = models.CharField(max_length=50, choices=BUILDING_TYPE_CHOICES, default='single_building')
#     total_share = models.PositiveIntegerField(default=0, help_text="Total ownership shares")
#     unit_per_floor = models.PositiveIntegerField(default=0)
    
#     # Amenities & Features (Boolean Fields for filtering)
#     has_lift = models.BooleanField(default=True, verbose_name="Lift/Elevator Available")
#     has_rooftop_access = models.BooleanField(default=True, verbose_name="Rooftop Facility")
#     has_convention_hall = models.BooleanField(default=False, verbose_name="Convention/Community Hall")
#     has_electricity_backup = models.BooleanField(default=True, verbose_name="Generator/Electricity Backup")
    
#     # Additional Details
#     total_units = models.PositiveIntegerField(default=0)
#     land_area = models.CharField(max_length=100, help_text="Example: 10 Katha")
#     handover_date = models.DateField(null=True, blank=True)
#     # cover_image = models.ImageField(upload_to='projects/covers/', null=True, blank=True)
#     cover_image = CloudinaryField('image', blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     def __str__(self):
#         return self.name




# class Property(models.Model):
    
#     # Basic Info
#     title = models.CharField(max_length=255)
#     description = models.TextField(blank=True, null=True)
#     unit_number = models.CharField(max_length=50)
#     size_sqft = models.DecimalField(max_digits=10, decimal_places=2)
#     floor_level = models.IntegerField()
#     price = models.DecimalField(max_digits=12, decimal_places=2)
#     status = models.CharField(max_length=15, default='available')
#     is_featured = models.BooleanField(default=False)

#     # Location / Road Info
#     road = models.CharField(max_length=255, blank=True, null=True)

#     # Room Details
#     bedroom = models.PositiveIntegerField(default=0)
#     bathroom = models.PositiveIntegerField(default=0)
#     balcony = models.PositiveIntegerField(default=0)

#     # Space Features
#     has_drawing_room = models.BooleanField(default=True)
#     has_dining_room = models.BooleanField(default=True)
#     has_kitchen = models.BooleanField(default=True)
#     has_garden = models.BooleanField(default=False)
#     has_hall = models.BooleanField(default=False)

#     # Facilities
#     has_lift = models.BooleanField(default=True)
#     has_parking = models.BooleanField(default=False)
#     has_electricity_backup = models.BooleanField(default=True)

#     project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='properties')

#     created_at = models.DateTimeField(auto_now_add=True)
#     # image = models.ImageField(upload_to='properties/images/', blank=True, null=True)
#     image = CloudinaryField('image', blank=True, null=True)


#     def __str__(self):
#         return f"{self.title} - {self.unit_number}"
    

#Blog Post

class BlogPost(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(help_text="Main content or description of the blog post")
    comments = models.TextField(blank=True, null=True, help_text="Comments or author notes")
    cover_image = models.ImageField(upload_to='blog/covers/', blank=True, null=True)
    # cover_image = CloudinaryField('image', blank=True, null=True)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    

class ClientReview(models.Model):
    client_name = models.CharField(max_length=255)
    review_text = models.TextField(blank=True, null=True, help_text="Client feedback or review")
    rating = models.PositiveSmallIntegerField(default=5, help_text="Rating out of 5")
    video = models.FileField(upload_to='client_reviews/videos/', blank=True, null=True)
    image = models.ImageField(upload_to='client_reviews/images/', blank=True, null=True)
    # cover_image = CloudinaryField('image', blank=True, null=True)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.client_name} - {self.rating}⭐"
    

class Message(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"