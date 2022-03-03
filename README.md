# House-Plant-BST

## Description:

The House Plant Buy / Sell / Trade site is a full-stack web application where
users can create accounts, buy, sell, or trade house plants, and upload
information about different house plants.

## Inspiration:

With more people taking a passionate interest in raising houseplants, this
project is an excellent resource for houseplant enthusiasts to find new plants
and trade or sell plants they have carefully raised.

## Technologies Used:

-   Python
-   Django
-   Bootstrap
-   JavaScript/jQuery
-   CSS/Html

## Prerequisites:

`python>=3.9 and django>=4.0.1`

Our project uses MariaDB, but feel free to use an alternative database setup:
https://docs.djangoproject.com/en/4.0/ref/settings/#databases

## Usage:

These instructions will get you a copy of the project up and running on your local machine for testing purposes.

### After cloning the repo, setup a virtual environment and activate it:

```
python -m venv venv
source venv/bin/activate
```

### Install required packages:

```
python -m pip install -r requirements.txt
```

<br>

### Next, setup a .env file with your MariaDB database information.

Please see the .env.example file as an example. The DB_USER name entered will need full permissions for the database. (Alternatively, you may modify the house_plant_bst/settings.py file to use the database of your choice. https://docs.djangoproject.com/en/4.0/ref/settings/#databases)

<br>

### Migrate the database.

From the main project folder which contains the manage.py file:

```
python manage.py makemigrations
python manage.py migrate
```

<br>

### To use the admin panel you can create a super user using the following command:

```
python manage.py createsuperuser
```

<br>

### To run the project:

```
python manage.py runserver
```

<br>

### Seed database:

Included in the repo files are some Plant data which you may use to seed the database if you like.

```
python manage.py runscript seed_db
```
