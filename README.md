pmgbilltracker
==============

Bill Tracking Application for the Parliamentary Monitoring Group.

The project consists of a user-facing website frontend and a backend API that handles the application logic.
An admin interface sits on top of the backend.

## What does this project do

The aim of the billtracker application is to supplement the PMG's existing website at http://pmg.org.za with a
set of pages that summarize all activity related to a particular bill. This includes committee meetings,
parliamentary debates, public hearings, etc.

By showing all of the activity related to a bill on a single page, it becomes easier for ordinary citizens to
understand the parliamentary process and make sense of the factors that influence a bill as it moves through
the houses of parliament.

The application's content is scraped automatically from the existing pmg website, but it can also be managed
manually through an admin interface.

## How it works

The billtracker can be found at http://bills.pmg.org.za. The admin-interface for managing the application's content,
is hosted at http://bills-api.pmg.org.za/admin.

## Contributing to the project

This project is open-source, and anyone is welcome to contribute. If you just want to make us aware of a bug / make
a feature request, then please add a new GitHub Issue (if a similar one does not already exist).

If you want to contribute to the code, please fork the repository, make your changes, and create a pull request.

### Local setup

To run this application in your local environment, use the builtin Flask dev-server:

1. Navigate into the application folder and install the required Python packages:

        cd pmgbilltracker
        sudo pip install -r requirements/local.txt

2. Run the dev server. First for the backend application:

        python runserver_backend.py

3. Open a new terminal, and do the same for the frontend application:

        cd pmgbilltracker
        python runserver_frontend.py


The frontend application should now be running at `http://localhost:5000/`, and the backend at `http://localhost:5001/`.


### Deploy instructions

To deploy this application to an Ubuntu 12.04 instance, which you can access via SSH:

1. Install the 'fabric' package for interacting with servers via ssh:

        sudo pip install fabric

2. Set up the relevant config paramenters for your server in `fabdefs.py`.

3. Navigate into the application folder and run the server setup and deploy scripts:

        cd pmgbilltracker
        fab <server_name> setup
        fab <server_name> deploy
        fab <server_name> configure

More details about setup and deployment can be found in fabfile.py, the script that fabric runs during deployment.

### Maintenance

Schedule the scraper to update the database daily:

        fab <server_name> schedule_scraper

Cancel the daily scraping with:

        fab <server_name> unschedule_scraper

Logs can be found at:

* Flask:

        /var/www/pmgbilltracker/debug.log

* Nginx:

        /var/log/nginx/error.log
        /var/log/nginx/access.log

* Supervisor:

        /var/log/supervisor/bills_backend.log
        /var/log/supervisor/bills_backend_err.log