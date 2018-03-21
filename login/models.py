from django.db import models
from django.contrib.auth.models import User


class Sourcing(models.Model):
    name = models.TextField(max_length=255, null=False, blank=False)
    rss_url = models.URLField(max_length=300, null=False, blank=False)
    created_by = models.ForeignKey(User, related_name="created_sourcing_set", default=1, on_delete=models.CASCADE)
    updated_by = models.ForeignKey(User, related_name="updated_sourcing_set", default=1, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('rss_url', 'created_by')

    def __str__(self):
        return u'{0}'.format(self.name)


class Stories(models.Model):
    title = models.TextField(max_length=500)
    source = models.ForeignKey(Sourcing, null=True, blank=True, on_delete=models.CASCADE)
    pub_date = models.DateTimeField(null=True, blank=True)
    body_text = models.TextField(blank=True)
    url = models.URLField(max_length=1000, null=True, blank=True)

    def __unicode__(self):
        return u'{0}'.format(self.title)
