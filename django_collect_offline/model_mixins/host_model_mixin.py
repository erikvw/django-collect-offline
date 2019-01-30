from django.db import models


class HostModelMixin(models.Model):

    """Abstract class for hosts (either client or server).
    """

    hostname = models.CharField(max_length=200, unique=True)

    port = models.IntegerField(default="80")

    api_name = models.CharField(max_length=15, default="v1")

    format = models.CharField(max_length=15, default="json")

    authentication = models.CharField(max_length=15, default="api_key")

    is_active = models.BooleanField(default=True)

    last_sync_datetime = models.DateTimeField(null=True, blank=True)

    last_sync_status = models.CharField(
        max_length=250, default="-", null=True, blank=True
    )

    comment = models.TextField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.hostname}:{self.port}"

    def natural_key(self):
        return (self.hostname,)

    @property
    def url_template(self):
        return (
            f"http://{self.hostname}:{self.port}/django_collect_offline/"
            f"api/{self.api_name}/"
        )

    @property
    def url(self):
        return self.url_template.format(
            hostname=self.hostname, port=self.port, api_name=self.api_name
        )

    class Meta:
        abstract = True
