from django.db import models
import re   # the regex module
import datetime
from datetime import datetime
from dateutil.relativedelta import relativedelta

# custom manager overriding the object
class UserManager(models.Manager):
    def basic_validator(self, postData):

        errors = {}
        EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

        # add keys and values to errors dictionary for each invalid field
        if len(postData["first_name"]) < 2:
            errors["first_name"] = "First Name should be at least 2 characters"
        if len(postData["last_name"]) < 2:
            errors["last_name"] = "Last Name should be at least 2 characters"
        if "gender" not in postData or len(postData["gender"]) == 0:
            errors["gender"] = "Gender is required"
        if "usta_rating" not in postData or len(postData["usta_rating"]) == 0:
            errors["usta_rating"] = "USTA rating or approximate value is required"
        elif float(postData["usta_rating"]) > 6 or float(postData["usta_rating"]) < 2.5: 
            errors["usta_rating"] = "USTA Rating should be between 2.5 and 6.0 "
        if len(postData["birthdate"]) == 0:
            errors["birthdate"] = "Birthdate is required"
        elif (postData["birthdate"]) >=  datetime.now().strftime("%Y-%m-%d"):
            errors["birthdate"] = "Birthdate should be in the past"
        elif ( relativedelta(datetime.now(), datetime.strptime(postData['birthdate'], '%Y-%M-%d')).years) < 13.0:  
            errors["birthdate"] = "Age should be at least 13 years old for compliance."
        if len(postData["email"]) == 0:  
            errors["email"] = "Email is required and should be in valid email format"
        if not EMAIL_REGEX.match(postData["email"]):    # test whether a field matches the pattern            
                errors["email"] = "Invalid email address format"  
        if len(postData["phone"]) == 0:
            errors["phone"] = "Phone is required"
        if len(postData["city_location"]) == 0:
            errors["city_location"] = "Location city or town, is required"

        if len(postData["password"]) < 8:    
            errors["password"] = "Password should be at least 8 characters"
        if (postData["password"] != postData["password_confirm"]):
            errors["password"] = "Password entered should match with the Confirm Pw"
        return errors



# User Table/Class
class User(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    gender = models.CharField(max_length=1, default='M')
    usta_rating = models.FloatField(default=3.0)
    email = models.EmailField(max_length=255, unique=True)
    birthdate = models.DateField()
    phone = models.CharField(max_length=255, default="4255187154")
    city_location = models.CharField(max_length=30, default="Seattle")
    wins = models.IntegerField(default=0)
    loses = models.IntegerField(default=0)
    lastSeasonRank = models.IntegerField(default=100)
    rank = models.IntegerField(default=100)
    password = models.CharField(max_length=64)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
     
    objects = UserManager() 

    # Links to Challenge Table
    # challenges
    # opponents


class ChallengeManager(models.Manager):
    def basic_validator(self, postData):

        errors = {}
        
        # add keys and values to errors dictionary for each invalid field
        if len(postData["tennis_court_name"]) < 3:
            errors["tennis_court_name"] = "Tennis court is required."
        if len(postData["tennis_court_addr"]) < 3:
            errors["tennis_court_addr"] = "Tennis court address is required."
        if len(postData["game_date"]) == 0:
            errors["game_date"] = "Game Date is required."
        elif (postData["game_date"]) <  datetime.now().strftime("%Y-%m-%d"):
            errors["game_date"] = "Game Date should not be in the past"
        if len(postData["game_time"]) ==  0:
            errors["game_time"] = "Game Time is required."
        
        return errors

class Challenge(models.Model):
    tennis_court_name = models.CharField(max_length=50)
    tennis_court_addr = models.CharField(max_length=75)
    game_date = models.DateField()
    game_time = models.TimeField()
    comments = models.CharField(max_length=255)
    status = models.CharField(max_length=20)
    score  = models.CharField(max_length=20)
    game_result = models.CharField(max_length=10)
        
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
   
    created_by = models.ForeignKey(User, related_name="challenges", on_delete = models.CASCADE) 
    against = models.ForeignKey(User, related_name="opponents", on_delete = models.CASCADE) 
 
    objects = ChallengeManager() 

  