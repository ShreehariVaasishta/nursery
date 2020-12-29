# Nursery Market

**Requirements**<br>
Please Refer [requirements.txt](https://github.com/ShreehariVaasishta/nursery/blob/dev_2/requirements.txt)

## Installation
**- Setup virtualenv**
  
  Please refer [Virtual environment setup by Django girls](https://tutorial.djangogirls.org/en/django_installation/#virtual-environment)
  
**install requirements**
    
          pip install requirements.txt

**setup**

-  Create a <b>PostgreSQL database.</b> and assign values for these in `settings.py` file.<br>
          
        SECRET_KEY = <your_django_secret_key>
        NAME = <database_name>
        USER = <database_user>
        PASSWORD = <database_password>
        HOST = <database_host>
        PORT = <database_port>

-  Migrate database
  
```python
        python3 manage.py makemigrations
        python3 manage.py migrate
```    
  <i>NOTE: if `makemigrations` show no migrations when trying for the first time migrate each app one after the other(Migrate user_management app first and then rest of the apps for overriding django user model with our custom user model.</i>
    
```python
        python3 manage.py makemigrations <app_name>
        example - python3 manage.py makemigrations user_management
``` 

-  Run server
  
```python
        python3 manage.py runserver
```    

-  Create a superuser for accessing admin panel
  http://localhost:8000/api/admin/
  
```python
        python3 manage.py createsuperuser
```  
   enter email, name and password and start the server again.


## Misc

 - Import this postman collection in your postman desktop app  https://www.getpostman.com/collections/b9f2a4f0a382d8b054dc  for list of endpoints with their description.<br>
   Also you can use https://dphi-nursery-sde.herokuapp.com/api/docs/

 - Getting the following error ?
        `AttributeError  'Nursery' object has no attribute 'IsBuyer' `   OR
        `AttributeError  'Buyer' object has no attribute 'IsNursery' `
        
   Fix - Please check your request token.
