from django.db import models
from django.contrib.auth.models import User

# Create your models here.

#
# class Subscription(models.Model):
#     username = models.CharField(max_length=50, null=False, blank=False, unique=True)
#     password = models.CharField(max_length=50, null=False, blank=False)
#     email = models.EmailField(null=False, blank=False)
#     fname = models.TextField(max_length=255, null=False, blank=False)
#     lname = models.TextField(max_length=255, null=False, blank=False)
#
#     def __unicode__(self):
#         return self.username


class Sourcing(models.Model):
    name = models.TextField(max_length=255, null=False, blank=False)
    rss_url= models.URLField(max_length=300, null=False, blank=False)
    created_by = models.ForeignKey(User, related_name="created_sourcing_set", default=15, on_delete=models.CASCADE)
    updated_by = models.ForeignKey(User, related_name="updated_sourcing_set", default=15, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)


    def __unicode__(self):
        return self.name


class Stories(models.Model):
    title = models.TextField(max_length=500)
    source = models.ForeignKey(Sourcing, null=True, blank=True, on_delete=models.CASCADE)
    pub_date = models.DateTimeField(null=True, blank=True)
    body_text = models.TextField(blank=True)
    url = models.URLField(max_length=1000, null=True, blank=True)

    def __unicode__(self):
        return self.title