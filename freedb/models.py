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
        return f'{self.owner}.{self.name}'


class Collection(models.Model):
    database = models.ForeignKey(Database, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    actual_col_name = models.CharField(max_length=50, null=True)

    def __str__(self):
        return f'{self.database}.{self.name}'

    class Meta:
        unique_together = [
            ['database', 'name'],
        ]


class Field(models.Model):
    collection = models.ForeignKey(Collection, null=False, on_delete=models.CASCADE)
    field_name = models.CharField(max_length=50)
    field_type = models.CharField(max_length=30)
    sort_no = models.IntegerField()
