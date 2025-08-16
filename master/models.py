from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class Module(models.Model):
    module = models.CharField(max_length=255)
    moduleType = models.CharField(max_length=255,default=1)
    url = models.CharField(max_length=255,blank=True)
    status = models.CharField(max_length=255,default=1)
    parent_id = models.CharField(max_length=255,blank=True)
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.module

class Role(models.Model):
    name = models.CharField(max_length=100)
    status = models.CharField(max_length=100)

class Access(models.Model):
    user =  models.ForeignKey(User, on_delete=models.CASCADE,related_name='roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE,related_name='role')
    assign = models.TextField(null=True, blank=True)
    given = models.ForeignKey(User, on_delete=models.CASCADE,related_name='given',null=True,blank=True,default=None)
    
class Permission(models.Model):
    role = models.ForeignKey(Role,on_delete=models.CASCADE)
    modules = models.ForeignKey(Module,on_delete=models.CASCADE)
    module_parent_id = models.CharField(max_length=255,blank=True)
    permission = models.CharField(max_length=255)
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.permission