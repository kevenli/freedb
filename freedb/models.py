from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Database(models.Model):
    name = models.CharField(max_length=20)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = [
            ['owner', 'name'],
        ]

    def __str__(self):
        return f'{self.name}.{self.owner}'

class Collection(models.Model):
    database = models.ForeignKey(Database, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.database}.{self.name}'

    class Meta:
        unique_together = [
            ['database', 'name'],
        ]