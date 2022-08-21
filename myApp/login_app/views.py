from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages
import bcrypt
import datetime
from datetime import datetime
from dateutil.relativedelta import relativedelta

# enable cryptography
# from cryptography.fernet import Fernet
import base64
import logging
import traceback
from django.conf import settings

# used for sending text and email
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# other imports
from .models import User, Challenge

# display sign-on/registration and login screen


def index(request):
    if "user_id" not in request.session:
        request.session["user_id"] = ''

    request.session["user_id"] = ''

    return render(request, "index.html")

# add the user to the database


def create(request):

    # pass the post data to the method we wrote and save the response in a variable called errors
    errors = User.objects.basic_validator(request.POST)

    # check if the errors dictionary has anything in it
    if len(errors) > 0:
        # if the errors dictionary contains anything, loop through each key-value pair and make a flash message
        for key, value in errors.items():
            messages.error(request, value)

        # redirect the user back to the form to fix the errors
        return redirect('/')
    else:
        try:
            # hash the password so it is unreadable
            hashed_pw = bcrypt.hashpw(
                request.POST["password"].encode(),
                bcrypt.gensalt()
            ).decode()

            # encrypt the phone so it is also unreadable
            #print('trying to perform encryption...')
            #encrypted_phone = encrypt(request.POST["phone"])
            #print('encrypted phone:', encrypted_phone)

            # insert into the database Table
            user = User.objects.create(
                first_name=request.POST["first_name"],
                last_name=request.POST["last_name"],
                email=request.POST["email"],
                gender=request.POST["gender"],
                birthdate=request.POST["birthdate"],
                usta_rating=float(request.POST["usta_rating"]),
                phone=request.POST["phone"],
                city_location=request.POST["city_location"],
                password=hashed_pw,
            )

            request.session["user_id"] = user.id

            # redirect to the dashboard
            return redirect('/dashboard')

        except:

            messages.error(request, "This email is not available")
            # redirect the user back to the form to fix the errors
            return redirect('/')


# use authentication to process log-in
def login(request):

    # try to find the user in the Database
    possible_users = User.objects.filter(email=request.POST["email"])

    if len(possible_users) == 0:

        messages.error(request, "Invalid email or password")
        return redirect('/')

    # compare the pwd entered with the hashed pwd in the Table
    if bcrypt.checkpw(
        request.POST["password"].encode(),
        possible_users[0].password.encode()
    ):
        request.session["user_id"] = possible_users[0].id
        return redirect('/dashboard')
    else:
        messages.error(request, "Invalid email or password")
        return redirect('/')


# log-out routine
def logout(request):

    request.session.clear()

    return redirect('/')

# display


def display_user(request, user_id):
    if (("user_id" not in request.session) or
            (request.session["user_id"] == '')):
        messages.error(request, "Please log-in first")
        return redirect('/')

    # pass the specific info, user info via context
    this_player = User.objects.get(id=user_id)
    age = relativedelta(datetime.now(), this_player.birthdate).years

    # 
    player_phone = this_player.phone
    print('Player phone:', player_phone)

    context = {"this_player": this_player,
               "age": age,
               "player_phone": player_phone,
               "this_user": User.objects.get(id=request.session["user_id"])
               }

    return render(request, "display_user.html", context)

#


def dashboard(request):
    if (("user_id" not in request.session) or
            (request.session["user_id"] == '')):
        messages.error(request, "Please log-in first")
        return redirect('/')

    user = User.objects.get(id=request.session["user_id"])
    user_gender = user.gender

    if (user_gender == 'M'):
        tournament_group = "Men's"
    else:
        tournament_group = "Women's"

    # recalculate ranking based on wins/loses
    user_gender = user.gender
    all_players = User.objects.filter(
        gender=user_gender).order_by('-wins', 'loses')
    i = 0
    for player in all_players:
        i += 1
        player.rank = i
        player.save()

    context = {
        "tournament_group": tournament_group,
        "all_players": User.objects.filter(gender=user_gender).order_by('-wins', 'loses'),
        "this_user": user
    }

    return render(request, "dashboard.html", context)

#  Add a new challenge


def add_challenge(request, opponent_id):
    if (("user_id" not in request.session) or
            (request.session["user_id"] == '')):
        messages.error(request, "Please log-in first")
        return redirect('/')

    # pass all the  info via context

    context = {"opponent_user": User.objects.get(id=opponent_id),
               "this_user": User.objects.get(id=request.session["user_id"])
               }

    return render(request, "add_challenge.html", context)


def create_challenge(request, opponent_id):
    # pass the post data to the method we wrote and save the response in a variable called errors
    errors = Challenge.objects.basic_validator(request.POST)

    # check if the errors dictionary has anything in it
    if len(errors) > 0:
        # if the errors dictionary contains anything, loop through each key-value pair and make a flash message
        for key, value in errors.items():
            messages.error(request, value)

        # redirect the user back to the form to fix the errors
        return redirect(f'/tennis/{opponent_id}/new')
    else:

        # create trip
        user = User.objects.get(id=request.session["user_id"])
        opponent_player = User.objects.get(id=opponent_id)
        challenge = Challenge.objects.create(
            tennis_court_name=request.POST["tennis_court_name"],
            tennis_court_addr=request.POST["tennis_court_addr"],
            game_date=request.POST["game_date"],
            game_time=request.POST["game_time"],
            comments=request.POST["comments"],
            status="Created",
            created_by=user,
            against=opponent_player

        )

        # send text message
        # send_text(request, challenge.id)

        # send email message
        # send_email(request, challenge.id)

        return redirect(f'/dashboard')


""" def encrypt(txt):
    try:
        # convert integer etc to string first
        txt = str(txt)

        # get the key from settings
        f = Fernet(settings.ENCRYPT_KEY)  # key should be byte

        # encode to bytes then encrypt
        encrypted_text = f.encrypt(txt.encode('ascii'))

        # encode to urlsafe base64 format
        encrypted_text = base64.urlsafe_b64encode(
            encrypted_text).decode("ascii")

        return encrypted_text
    except Exception as e:
        # log the error if any
        logging.getLogger("error_logger").error(traceback.format_exc())
        return None


def decrypt(txt):
    try:
        # base64 decode
        txt = base64.urlsafe_b64decode(txt)

        # get the key from settings.py
        f = Fernet(settings.ENCRYPT_KEY)

        # decrypt
        decoded_text = f.decrypt(txt).decode("ascii")

        return decoded_text

    except Exception as e:
        # log the error
        logging.getLogger("error_logger").error(traceback.format_exc())
        return None """


def send_text(request, challenge_id):

    # Make sure these are also added on top
    #
    # used for sending text
    #   import smtplib
    #   from email.mime.text import MIMEText
    #   from email.mime.multipart import MIMEMultipart

    challenge = Challenge.objects.get(id=challenge_id)

    email = "rm@gmail.com"  # email on google
    pas = "mypassword"        # password for the email

    # SMS Gateways for each Carrier
    #    AT&T: [number]@txt.att.net
    #    Sprint: [number]@messaging.sprintpcs.com or [number]@pm .sprint.com
    #    T-Mobile: [number]@tmomail.net
    #    Verizon: [number]@vtext.com
    #    Boost Mobile: [number]@myboostmobile.com
    #    Cricket: [number]@sms.mycricket.com
    #    Metro PCS: [number]@mymetropcs.com
    #    Tracfone: [number]@mmst5.tracfone.com
    #    U.S. Cellular: [number]@email.uscc.net
    #    Virgin Mobile: [number]@vmobl.com

    sms_gateway = '1234561111@messaging.sprintpcs.com'

    # The server we use to send emails in our case it will be gmail but every email provider has a different smtp
    # and port is also provided by the email provider.
    smtp = "smtp.gmail.com"
    port = 587

    # This will start our email server
    server = smtplib.SMTP(smtp, port)

    # Starting the server
    server.starttls()

    # Now we need to login
    server.login(email, pas)

    # Now we use the MIME module to structure our message.
    msg = MIMEMultipart()
    msg['From'] = email
    msg['To'] = sms_gateway

    # Make sure you add a new line in the subject
    msg['Subject'] = f"Puget Sound Tennis Tour - Challenge \n"

    # Make sure you also add new lines to your body
    body = f"You have a tennis challenge vs {challenge.created_by.first_name} on {challenge.game_date} \n"

    # and then attach that body furthermore you can also send html content.
    msg.attach(MIMEText(body, 'plain'))

    sms = msg.as_string()

    server.sendmail(email, sms_gateway, sms)

    # lastly quit the server
    server.quit()

    return


def send_email(request, challenge_id):

    # Make sure these are also added on top
    #
    # used for sending email
    #
    #   import smtplib
    #   from email.mime.text import MIMEText
    #   from email.mime.multipart import MIMEMultipart

    challenge = Challenge.objects.get(id=challenge_id)

    mail_content = f"A friendly reminder from Puget Sound Tennis Tour. You have a challenge from {challenge.created_by.first_name} on {challenge.game_date} "

    # The mail addresses and password
    sender_address = "rm@gmail.com"
    sender_pass = "mypassword"
    receiver_address = 'rm@gmail.com'

    # Setup the MIME
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = receiver_address
    # The subject line
    message['Subject'] = 'Puget Sound Tennis Tour - Challenge '

    # The body and the attachments for the mail
    message.attach(MIMEText(mail_content, 'plain'))

    # Create SMTP session for sending the mail
    session = smtplib.SMTP('smtp.gmail.com', 587)  # use gmail with port
    session.starttls()  # enable security
    # login with mail_id and password
    session.login(sender_address, sender_pass)

    text = message.as_string()
    session.sendmail(sender_address, receiver_address, text)

    session.quit()

    print('Mail Sent')
    return


def edit_challenge(request, challenge_id):
    if (("user_id" not in request.session) or
            (request.session["user_id"] == '')):
        messages.error(request, "Please log-in first")
        return redirect('/')

    # pass the info via context
    context = {"this_challenge": Challenge.objects.get(id=challenge_id),
               "this_user": User.objects.get(id=request.session["user_id"])
               }

    return render(request, "edit_challenge.html", context)

# update Table


def update_challenge(request, challenge_id):

    # pass the post data to the method we wrote and save the response in a variable called errors
    errors = Challenge.objects.basic_validator(request.POST)

    # check if the errors dictionary has anything in it
    if len(errors) > 0:
        # if the errors dictionary contains anything, loop through each key-value pair and make a flash message
        for key, value in errors.items():
            messages.error(request, value)

        # redirect the user back to the form to fix the errors
        return redirect(f'/tennis/{challenge_id}/edit')
    else:
        user = User.objects.get(id=request.session["user_id"])
        challenge = Challenge.objects.get(id=challenge_id)

        # update dB fields with form fields and save
        challenge.tennis_court_name = request.POST["tennis_court_name"]
        challenge.tennis_court_addr = request.POST["tennis_court_addr"]
        challenge.game_date = request.POST["game_date"]
        challenge.game_time = request.POST["game_time"]
        challenge.comments = request.POST["comments"]

        challenge.save()

        return redirect('/dashboard')


def add_game_result(request, challenge_id):
    if (("user_id" not in request.session) or
            (request.session["user_id"] == '')):
        messages.error(request, "Please log-in first")
        return redirect('/')

    # pass the info via context
    context = {"this_challenge": Challenge.objects.get(id=challenge_id),
               "this_user": User.objects.get(id=request.session["user_id"])
               }

    return render(request, "report_game_result.html", context)

# update Challenge and User Table


def create_result(request, challenge_id):

    # pass the post data to the method we wrote and save the response in a variable called errors
    errors = Challenge.objects.basic_validator(request.POST)

    # check if the errors dictionary has anything in it
    if len(errors) > 0:
        # if the errors dictionary contains anything, loop through each key-value pair and make a flash message
        for key, value in errors.items():
            messages.error(request, value)

        # redirect the user back to the form to fix the errors
        return redirect(f'/tennis/{challenge_id}/results')
    else:
        user = User.objects.get(id=request.session["user_id"])
        challenge = Challenge.objects.get(id=challenge_id)

        # update dB fields with form fields and save
        challenge.status = 'Played'
        challenge.score = request.POST["score"]
        challenge.game_result = request.POST["game_result"]
        challenge.save()

        # update Player Table: challenger and opponent

        challenger = challenge.created_by
        if int(request.POST["game_result"]) == 1:
            challenger.wins += 1
        else:
            challenger.loses += 1
        challenger.save()

        opponent = challenge.against
        if int(request.POST["game_result"]) == 1:
            opponent.loses += 1
        else:
            opponent.wins += 1
        opponent.save()

        # recalculate the Rankings for the same tournament group (Men's or Women's)
        user_gender = user.gender
        all_players = User.objects.filter(
            gender=user_gender).order_by('-wins', 'loses')
        i = 0
        for user in all_players:
            i += 1
            user.rank = i
            user.save()

        return redirect('/dashboard')


# display
def display_challenge(request, challenge_id):
    if (("user_id" not in request.session) or
            (request.session["user_id"] == '')):
        messages.error(request, "Please log-in first")
        return redirect('/')

    # pass the specific info, user info via context

    context = {"this_challenge": Challenge.objects.get(id=challenge_id),

               "this_user": User.objects.get(id=request.session["user_id"])
               }

    return render(request, "display_challenge.html", context)

# delete


def delete_challenge(request, challenge_id):
    challenge = Challenge.objects.get(id=challenge_id)
    challenge.delete()

    return redirect('/dashboard')

# accept challenge


def accept_challenge(request, challenge_id):
    challenge = Challenge.objects.get(id=challenge_id)
    if (challenge.status != 'Played'):
        challenge.status = "Accepted"
        challenge.save()

    return redirect('/dashboard')

# reject challenge


def reject_challenge(request, challenge_id):
    challenge = Challenge.objects.get(id=challenge_id)
    if (challenge.status != 'Played'):
        challenge.status = "Rejected"
        challenge.save()

    return redirect('/dashboard')


# report scores - games have been played
def report_scores(request, challenge_id):
    challenge = Challenge.objects.get(id=challenge_id)
    if (challenge.status != 'Rejected'):
        challenge.status = "Played"
        challenge.save()

    return redirect('/dashboard')
