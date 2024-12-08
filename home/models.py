from django.db import models

# Create your models here.
class FlowData(models.Model):
    
    name = models.CharField(max_length=100)
    data = models.JSONField()
    prediction = models.CharField(max_length=100,default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name