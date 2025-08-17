from django.db import models
from django.contrib.auth.models import User
class Posts(models.Model):

    FILE_TYPE_CHOICES = [
        (1, 'File'),
        (2, 'Folder'),
    ]
    name = models.TextField()
    image = models.TextField()
    rate = models.DecimalField(max_digits=5, decimal_places=2)
    size = models.CharField(max_length=100)
    lang = models.TextField()
    genre = models.TextField()
    story = models.TextField()
    link = models.CharField(max_length=100)
    type = models.IntegerField(choices=FILE_TYPE_CHOICES, default=1)
    duration=models.TextField(null=True, blank=True)
    more = models.TextField()
    parent = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=100)
    starcast=models.TextField()
    menu=models.TextField(null=True, blank=True)
    trand = models.IntegerField(default=0)
    release_date=models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    updated_at = models.DateTimeField(auto_now=True,null=True,blank=True)
    

class Menu(models.Model):
    FILE_TYPE_CHOICES = [
        (1, 'File'),
        (2, 'Folder'),
    ]
    name = models.CharField(max_length=100)
    menuId = models.CharField(max_length=100,null=True)
    type = models.IntegerField(choices=FILE_TYPE_CHOICES, default=1)
    link = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=100)

class Comments(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(Posts, on_delete=models.CASCADE, related_name='comments')
    #user =  models.OneToOneField(Customer, on_delete=models.CASCADE,related_name='customer')
    msg = models.TextField(blank=True, null=True)
    #post = models.OneToOneField(Posts, on_delete=models.CASCADE,related_name='post')
    parentId = models.CharField(max_length=100,null=True)
    status = models.CharField(max_length=100,default='0')
    created_at = models.DateField(auto_now_add=True)

class MailMessage(models.Model):
    subject =  models.CharField(max_length=200,null=True)
    to_address = models.EmailField(max_length=100)
    from_address = models.EmailField(max_length=100)
    content =  models.TextField(blank=True, null=True)