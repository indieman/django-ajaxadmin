from django.db import models


class TempFile(models.Model):
    file = models.FileField(upload_to='temp')
    key = models.CharField(max_length=50)
    model_name = models.CharField(max_length=200)

