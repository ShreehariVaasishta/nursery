from django.db import models
from django.utils.translation import ugettext_lazy as _
import uuid
from user_management.models import Nursery, Buyer
from django.utils import timezone

# Create your models here.
def image_upload_path(instance, filename):
    return "files/plants/images/user_{0}/{1}".format(instance.id, filename)


class Plants(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("Plant Name"), max_length=100, blank=False, null=False)
    owner = models.ForeignKey(Nursery, blank=False, null=False, on_delete=models.CASCADE)
    image = models.FileField(upload_to=image_upload_path, blank=True, null=True)
    plant_description = models.TextField(_("Plant Description"), max_length=200)
    price = models.DecimalField(max_digits=5, decimal_places=2, blank=False, null=False)
    inStock = models.BooleanField(default=True)
    isDeleted = models.BooleanField(default=False)

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = _("Nursery - Plants")
        verbose_name_plural = _("Nursery - Plants")

    def __str__(self):
        return self.name

    @property
    def get_image_path(self):
        return self.image.path
