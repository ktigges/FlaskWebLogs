Script with a web front end that queries panorama traffic logs and displays results
This script uses Flask and the WTForms framework to display input fields and render the results
For this script to run we need some pre-requisites

The requirements are listed in the requirements.txt file

blinker==1.6.2
certifi==2023.5.7
cffi==1.15.1
charset-normalizer==3.1.0
click==8.1.3
cryptography==41.0.1
Flask==2.3.2
Flask-WTF==1.1.1
idna==3.4
itsdangerous==2.1.2
Jinja2==3.1.2
MarkupSafe==2.1.3
pycparser==2.21
requests==2.31.0
urllib3==2.0.3
Werkzeug==2.3.6
WTForms==3.0.1


Directory Structure that needs to be present

App Folder
     static
          css
              style.css
     templates
         index.html
         results.html
    apikey.txt
    apipass.txt
    cert.pem
    key.pem
    panologquery.py
    query.py
    .flaskenv


The script uses an API key to make request calls to Panorama

There is an ancillary script called encrypt_api.py that will create an encrypted copy of the API key on disk, as well as a key utilized to derrive the actual key.  While not government
level encryption, it does keep the key from prying eyes if they have access to the file system.

To create the encrypted API key combination, place the API key in a file called api.txt, then just run the encrypt_api.py script and it will generate 2 files
apikey.txt and apipass.txt that will be used in the program.  It will delete the api.txt file once completed.

There is a file called config.options that contains 2 entries
    The Panorama IP we will be querying
    Do we want to enable SSL to the web front end

    The format is scrict and should be as follows in the order below:

        panorama_ip=192.168.254.5
     

If SSL encryption is to be used, you will need to place your certificate and private key in PEM format in the program directory, and name them cert.pem and key.pem
    You can use self signed or a CA issued cert.  If you don't know how to generate a public/private key pair - then google that

Modify the .flaskenv file to match your preferences for SSL, Port and Listening IP.  You can set debug here as well if needed.

The program in it's current state, takes 4 options

    IP Address to query for
    A reference Time for the query
    The number of minutes to look back from your reference time.
    An optional Port to search for

    (We can modify any of these to add any other information to the query)



To run the script

    1. Create a Python Virtual Environment for this code
    2. Download the github repository (or the individual files above if you just want this script)
    3. Install the requirements -- pip install -r requirements.txt
    4. Update your panorama IP in the config.options and set SSL to yes or now
    5. If using SSL, then make sure you have a cert.pem and cert.key for this app
    6. get your panorama API key (use google to find out how to get this), and place it in the api.txt file (that you need to create)
    6. run python3 ./encrypt_api.py and it will create the api key files needed
    7. run the app and see if it works -- python3 ./


You can also run this in a docker container using the following dockerfile or your own modified version:

# syntax=docker/dockerfile:1

FROM python:3.9-slim-buster

WORKDIR /panologquery

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .
EXPOSE 5300

CMD ["python3", "-m", "flask", "run"]

