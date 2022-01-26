from django.db import models


class Plant(models.Model):
    scientific_name = models.CharField(max_length=150)
    description = models.TextField()
    plant_care = models.TextField()

    class Meta:
        verbose_name_plural = 'Plants'

    def __str__(self):
        """String for representing the Plant object (ex: the Admin site). """
        return self.scientific_name


class PlantCommonName(models.Model):
    name = models.CharField(max_length=150)
    plant_id = models.ForeignKey(Plant, verbose_name="Plant",
                                 on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'Plant Common Names'

    def __str__(self):
        """String for representing the Plant object (ex: the Admin site). """
        return self.name

