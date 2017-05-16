# zomato_email_alerts
Email alerts for negative reviews on Zomato

## Dependency
* MySQL
  
  Please install and setup MySQL and use the username and password in the config file.

  Make sure mysql server is up and running before moving further.

## Update config file
* Get Zomato API key
* Get SendGrid API key
* Edit the config file to change the email sender and recipient
* Edit the config file to add MySQL username and password

## Configure and setup the repository
### Unix

#### Run the following commands on a Unix Shell
* pip install virtualenv

Create a new virtual environment

* python -m virtualenv </path/to/virtualenv/virtualenvname>
* cd </path/to/virtualenv/virtualenvname>
* source bin/activate

Copy the cloned repository in the virtualenv folder just created using the following -

* cd <cloned_repository>/scripts

Copy the Sendgrid API key in the command below - 

* echo "export SENDGRID_API_KEY= '<YOUR_API_KEY>' " > sendgrid.env

<!-- Set up cronjob for periodically running the script. -->
<!-- Runs the script and checks for negative reviews every Tuesday, Wednesday and Thursday at 0000hrs -->
* crontab -e

  _Copy and paste the following in the editor that opens up -_
  
  0 0 * * 2,3,4 /usr/bin/python /path/to/your/script.py >/dev/null 2>&1

* sudo apt-get install python-pip python-dev libmysqlclient-dev
* pip install -r requirements.txt
* python get_reviews.py

### Windows
TODO

### MAC OS X
TODO