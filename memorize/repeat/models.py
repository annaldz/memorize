from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator

STAT= (
    ('e', 'Empty'),
    ('n', 'Normal'),
    ('h', 'Hard'),
    ('s', 'Simple'),
    ('o', 'Old'),
    ('x', 'Extra_old'),
)

class Flashcard(models.Model):
    list_id = models.ForeignKey('List')
    question = models.CharField(max_length=200)
    answer = models.CharField(max_length=500)
    created_date = models.DateTimeField(
            default=timezone.now)
    repeat_date = models.DateTimeField(
            blank=True, null=True)
    difficulty = models.FloatField(default = 1.0)
    
    def __str__(self):
        return self.question

class List(models.Model):
      owner = models.ForeignKey(User)
      name = models.CharField(max_length=250)
      limit = models.PositiveIntegerField(
          default = 30, 
          validators=[
              MaxValueValidator(500),
              MinValueValidator(5)
          ]
      )
      status = models.CharField(max_length=1, choices=STAT, default='e')
      
      def __str__(self):
          return self.name  
    


