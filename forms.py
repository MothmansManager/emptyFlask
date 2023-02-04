from logging import PlaceHolder
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, IntegerField, RadioField
from wtforms.validators import InputRequired, EqualTo, NumberRange, Length
#form for login. reads in user_id, password.
class loginForm(FlaskForm):
    user_id = StringField("User Name:", validators = [InputRequired()])
    password= PasswordField("Enter Password:", validators = [InputRequired()])
    submit = SubmitField("Submit")
    
#form for the registration page, reads in user_id, compares password is equal and verifies user is over 18.
class regForm(FlaskForm):
    user_id = StringField("User Name:", validators = [InputRequired()])
    age = IntegerField("Age:",  
                validators = [InputRequired(), NumberRange(18)])
    password1= PasswordField("Enter Password:", 
                validators = [InputRequired()])
    password2= PasswordField("Confirm Password:", 
                validators = [InputRequired(), EqualTo("password1")])
    submit = SubmitField("Submit")



#form for setting up ones account details/profile on the site.
class profileSetupForm(FlaskForm):
    icon = RadioField("Choose an icon:",
        choices = ["Snake", "Daisy", "Monstera", "Cactus", "leaf"],
        default = ["Snake"])
    first_name = StringField("First Name*:", validators = [InputRequired(), Length(max=12)])
    gender = RadioField("I am:",
        choices = ["Male", "Female", "Non-Binary", "Agender", "Prefer Not to Say"],
        default = "Prefer Not to Say")
    bio = StringField("Bio (<300 chars.):", validators = [Length(max=300)])
    submit = SubmitField("Save Changes")


