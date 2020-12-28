from django.db import models
from django.utils.translation import ugettext_lazy as _
import uuid
from user_management.models import Nursery, Buyer
from django.utils import timezone

# Create your models here.
def image_upload_path(instance, filename):
    return "files/plants/images/user_{0}/{1}".format(instance.id, filename)


class Plants(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    name = models.CharField(_("Plant Name"), max_length=100, blank=False, null=False)
    owner = models.ForeignKey(Nursery, blank=False, null=False, on_delete=models.CASCADE)
    image = models.FileField(upload_to=image_upload_path, blank=True, null=True)
    plant_description = models.TextField(_("Plant Description"), max_length=200)
    price = models.DecimalField(max_digits=5, decimal_places=2, blank=False, null=False)
    inStock = models.BooleanField(default=True)
    isDeleted = models.BooleanField(default=False, db_index=True)

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ("created_at",)
        verbose_name = _("Nursery - Plants")
        verbose_name_plural = _("Nursery - Plants")

    def __str__(self):
        return self.name

    @property
    def get_image_path(self):
        if not self.image:
            return None
        return self.image.path


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    plant = models.ForeignKey(Plants, on_delete=models.CASCADE, blank=False, null=False)
    user = models.ForeignKey(Buyer, on_delete=models.Case, blank=False, null=False)
    quantity = models.PositiveIntegerField()
    total = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ("created_at",)
        verbose_name = _("Nursery - Carts")
        verbose_name_plural = _("Nursery - Carts")

    def __str__(self):
        return f"{self.id}"

    def save(self, *args, **kwargs):
        self.total = self.plant.price * self.quantity
        super(Cart, self).save(*args, **kwargs)


class Order(models.Model):
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    ON_THE_WAY = "ON_THE_WAY"
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    ORDER_STATUS = [
        (DELIVERED, "Delivered"),
        (CANCELLED, "Cancelled"),
        (ON_THE_WAY, "On the way"),
        (PENDING, "Pending"),
        (CONFIRMED, "Confirmed"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    plant = models.ForeignKey(Plants, on_delete=models.CASCADE, blank=False, null=False)
    buyer = models.ForeignKey(Buyer, on_delete=models.Case, blank=False, null=False, help_text="Buyer")
    quantity = models.PositiveIntegerField()
    total = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    is_payed = models.BooleanField(default=False)
    order_status = models.CharField(_("Order Status"), max_length=10, choices=ORDER_STATUS, default=PENDING)

    ordered_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ("ordered_at",)
        verbose_name = _("Nursery - Orders")
        verbose_name_plural = _("Nursery - Orders")

    def __str__(self):
        return f"{self.id}"

    def save(self, *args, **kwargs):
        self.total = self.plant.price * self.quantity
        super(Order, self).save(*args, **kwargs)