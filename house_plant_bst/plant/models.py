from django.db import models
from django.conf import settings
from django.urls import reverse_lazy

User = settings.AUTH_USER_MODEL


class Plant(models.Model):
    scientific_name = models.CharField(max_length=150, unique=True)
    description = models.TextField(help_text='Describe the plant')
    plant_care = models.TextField(
        help_text='Share some care info\n'
        'Light:\n'
        'Water:\n'
        'Fertilizer:\n'
        'Temperature:\n'
        'Humidity:\n'
        'Soil:\n'
        'Pot:\n'
        'Pruning:\n'
        'Propagation:\n'
        'Poisonous Plant Info:\n'
    )

    class Meta:
        verbose_name_plural = 'Plants'

    def __str__(self):
        """String for representing the Plant object (ex: the Admin site)."""
        return self.scientific_name

    def get_absolute_url(self):
        """Returns the absolute url for plant object to view plant details"""
        return f'/plant/{self.pk}'

    def get_update_url(self):
        """Return the url to update plant"""
        return f'/plant/{self.pk}/update'

    def get_delete_url(self):
        """Returns the url to delete plant object"""
        return f'/plant/{self.pk}/delete'


class PlantCommonName(models.Model):
    """Each PlantCommonName instance object ties a common name to a Plant
    object"""

    name = models.CharField(max_length=150, verbose_name="Common Name")
    plant = models.ForeignKey(
        Plant,
        verbose_name='Plant',
        on_delete=models.CASCADE,
        related_name='get_common_names',
    )

    class Meta:
        verbose_name_plural = 'Plant Common Names'

    def __str__(self):
        return self.name


class UserPlant(models.Model):
    """Each UserPlant instance objects indicates a Plant to User relationship.
    Note that UserPlants should never be deleted, as they may need to persist
    in OrderItem data as well as TradeItem data."""

    user = models.ForeignKey(
        User,
        null=True,
        verbose_name='User',
        on_delete=models.SET_NULL,
        related_name='get_user_plants',
    )
    plant = models.ForeignKey(
        Plant,
        verbose_name='Plant',
        on_delete=models.RESTRICT,
        related_name='get_user_plants',
    )
    is_for_sale = models.BooleanField(default=False)
    is_for_trade = models.BooleanField(default=False)
    is_for_pickup = models.BooleanField(default=False)
    is_for_shipping = models.BooleanField(default=False)
    image_url = models.CharField(max_length=512, blank=True)
    quantity = models.PositiveSmallIntegerField(default=0)
    unit_price = models.DecimalField(
        max_digits=6, decimal_places=2, default=0.00
    )
    comment = models.TextField(
        blank=True, help_text='Share some info about your plant!'
    )

    class Meta:
        verbose_name_plural = 'User\'s Plants'

    def __str__(self):
        return f'owner: {self.user.username}, \
               plant: {self.plant.scientific_name}'

    def get_absolute_url(self):
        """Returns the absolute url for userplant object"""
        return reverse_lazy('plant:userplant_detail', kwargs={'pk': self.pk})

    def get_update_url(self):
        """Return the url to update plant"""
        return f'{self.pk}/update'

    def get_delete_url(self):
        """Returns the url to delete plant object"""
        return f'{self.pk}/delete'
