pmgbilltracker
==============

Bill Tracking Application for the Parliamentary Monitoring Group.

The project consists of two components: a frontend client application to demonstrate a user-facing website,
and a backend application that handles all of the application logic, and exposes the database through an API
and an admin interface.


SETUP FOR LOCAL ENVIRONMENT:
-----------------------
To run this application in your local environment, using the builtin Flask dev-server:

1. Navigate into the application folder and install the required Python packages:

        cd pmgbilltracker
        sudo pip install -r requirements/local.txt

2. Run the dev server. First for the backend application:

        python runserver_backend.py

3. Open a new terminal, and do the same for the frontend application:

        cd pmgbilltracker
        python runserver_frontend.py


The frontend application should now be running at `http://localhost:5000/`, and the backend at `http://localhost:5001/`.


DEPLOY INSTRUCTIONS:
-----------------------
To deploy this application to an Ubuntu 13.10 instance on AWS EC2:

1. Install fabric to handle deployment:

        sudo pip install fabric

2. Save the ssh key for the instance as `aws_code4sa.pem` in your `~/.ssh` directory.

3. Edit the `env.hosts` variable for the staging environment in fabfile.py to point to the correct instance.

4. Navigate into the application folder and run the server setup and deploy scripts:

        cd pmgbilltracker
        fab staging setup
        fab staging configure
        fab staging deploy_backend
        fab staging deploy_frontend

More details about setup and deployment can be found in fabfile.py, the script that fabric runs during deployment.

NOTES:
------
To access this server via SSH:

    ssh -v -i ~/.ssh/aws_code4sa.pem ubuntu@54.229.255.34

Error logs can be found at:

    tail -n 100 /var/log/apache2/error.log
    tail -n 100 /var/www/pmgbilltracker/debug.log