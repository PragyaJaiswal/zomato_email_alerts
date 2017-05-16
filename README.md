# zomato_email_alerts
Email alerts for negative reviews on Zomato

## Unix
### Run the following commands on a Unix Shell
* pip install virtualenv
* python -m venv </path/to/virtualenv/virtualenvname>
* cd </path/to/virtualenv/virtualenvname>
* source bin/activate

Copy the project folder(zomato_email_alerts) in the virtualenv folder just created.

* cd zomato_email_alerts/scripts
* echo "export SENDGRID_API_KEY= '<YOUR_API_KEY>' " > sendgrid.env

<!-- Set up cronjob for periodically running the script. -->
<!-- Runs the script and checks for negative reviews every Tuesday and Thursday at 0000hrs -->
* crontab -e

  _Copy and paste the following in the editor that opens up -_
  
  0 0 * * 2,3,4 /usr/bin/python /path/to/your/script.py > /home/someuser/cronlogs/clean_tmp_dir.log >/dev/null 2>&1

* pip install -r requirements.txt
* python get_reviews.py