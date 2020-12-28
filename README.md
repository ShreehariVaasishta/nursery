# Nursery Market

**Requirements**<br>
Please Refer [requirements.txt](https://github.com/ShreehariVaasishta/nursery/blob/dev_2/requirements.txt)

## Installation
**- Setup virtualenv**
  
  Please refer [Virtual environment setup by Django girls](https://tutorial.djangogirls.org/en/django_installation/#virtual-environment)
  
**install requirements**
    
          pip install requirements.txt

**setup**

-  Create a <b>PostgreSQL database.</b><br>
  create `.env` file in the project root directory and add following in the .env file:
  
        SECRET_KEY = #(#2oj20fqshsa)n!xc)9%^4w2b)4he5uih!yli@)rr%l4c^^g
        db_name = nursery_dphi
        db_user = hari
        db_user_password = Auden123
        

-  Migrate database
  
```python
        python3 manage.py makemigrations
        python3 manage.py migrate
```    
  <i>NOTE: if `makemigrations` show no migrations when trying for the first time migrate each app one after the other(Migrate user_management app first and then rest of the apps for overriding django user model with our custom user model.</i>
    
```python
        python3 manage.py makemigrations <app_name>
        python3 manage.py makemigrations user_management
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
   enter email, name and password and start server again.
