from django.db import models


class Greeting(models.Model):
    text = models.CharField(max_length=250, null=False, blank=False)

    def __str__(self):
        return f'Received greeting: {self.text}'
