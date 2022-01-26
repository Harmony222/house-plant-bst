from django.core.exceptions import ObjectDoesNotExist
from plant.models import Plant, PlantCommonName
import csv

plant_csv_path = r'../data/db_upload_plant.csv'
plant_common_name_csv_path = r'../data/db_upload_plant_common_name.csv'


def seed_plant_table(csv_path):
    with open(csv_path) as csv_file:
        reader = csv.DictReader(csv_file)
        reader_rows = list(reader)
        plant_objs = [
            Plant(
                scientific_name=row['scientific_name'],
                description=row['description'],
                plant_care=row['plant_care']
            )
            for row in reader_rows
        ]

    Plant.objects.bulk_create(plant_objs)


def seed_plant_common_name_table(csv_path):
    with open(csv_path) as csv_file:
        reader = csv.DictReader(csv_file)
        plant_common_name_objs = []

        for i, row in enumerate(reader):
            # if plant doesn't exist, skip this plant common name entry
            try:
                id = Plant.objects.get(scientific_name=row['scientific_name'])
            except ObjectDoesNotExist as e:
                print(e)
                break

            new_obj = PlantCommonName(
                name=row['name'],
                plant_id=id
            )
            plant_common_name_objs.append(new_obj)
        PlantCommonName.objects.bulk_create(plant_common_name_objs)


def run():
    seed_plant_table(plant_csv_path)
    seed_plant_common_name_table(plant_common_name_csv_path)


if __name__ == "__main__":
    run()
