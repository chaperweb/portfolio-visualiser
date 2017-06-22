# Portfolio visualizer

Portfolio visualizer is data visualization tool designed for portfolio management purposes.

Portfolio visualizer aims at creating a tool for collaborative, open and agile portfolio management. The idea is to build a tool which allows opening the portfolio information to every member of the organization and possibly also to the	customers. The tool helps in creating common understanding and in making decisions by visualizing the project in many formats

Portfolio visualizer's source code is made available under the [GNU General Public License v3]

Portfolio visualizer is being developed using [Django framework]

# Building
For easy start we recommend installing `python3` and `python3-pip` and after that continue with instructions given below.

Ensure that you have necessary libraries installed by running requirements.txt from the project root folder.
```
$ pip install -r requirements.txt
```
Setup the django models:
```
$ python3 manage.py makemigrations
$ python3 manage.py migrate
```
After these steps are successfully taken, you can run your local server version by typing:
```
$ python3 manage.py runserver
```
You can access the software from address `localhost:8000`, and for the admin access `localhost:8080`.

# Data input

TBA

# How to run tests

## In Jenkins

This will happen automatically each day and you don't want to be the cause for these to fail.

If you are a Codento developer, you'll get access to Jenkins for continuous build, testing and integration.
There the dashboard shows the status of the latest build, which is 'success' even when the tests fail -- status is
about the success of the build, you have to click it to see how the tests are doing.

The script to run tests uses the nice docker build system put in place by Joonas Harjumäki.

    #!/bin/bash
    #export WORKSPACE=`pwd`

    # Activate virtualenv
    source venv/bin/activate

    # Install Requirements
    pip install -r Development/visualizer/requirements.txt

    python Development/visualizer/manage.py makemigrations
    python Development/visualizer/manage.py migrate



    cd Development/visualizer/
    mkdir -p junit
    rm junit/*.xml
    docker build -t portfolio_visualiser .
    docker run --name portfolio_visualizer_tests portfolio_visualiser /app/run_tests.sh
    docker cp portfolio_visualizer_tests:/app/junit/ ./
    docker rm portfolio_visualizer_tests
    docker images -f dangling=true -q | xargs docker rmi

    sudo /sbin/service httpd reload

## Locally in Docker

You'll want to do this once before making a pull request.

The idea is to replicate what is happening in Jenkins, but also avoid running unnecessary costly operations.
If running tests is too slow or cumbersome, people will flake. Docker can make things stable, but with the price of making processes slow and cumbersome.  

Assume that we are already in project folder. We probably have virtualenv running, if not, then:

    source venv/bin/activate

Docker should be running. In macOS, Docker's official app will have its whale icon on top right icon bar, and docker is running. There is also Kitematic.app installed for GUI to manage containers. You'll need it if your Docker container ends up stuck or broken, or you otherwise need to free space from unused containers and images.

### Building test image

With docker, build an image:

    docker build -t portfolio_visualiser .

This will take a while for the first time, subsequent calls will be faster as the images used for build and intermediate
build stages are cached. It is necessary to always *build* before running docker tests, as the subsequent container will have the current code. `-t portfolio_visualiser` tags the built image with given name, so we can find it. `.` at the end is easy to miss, but it is necessary: Build by using the Dockerfile found here in this folder.

What you have built is not specifically a *test* container, it is just portfolio_visualiser project put into a container with Linux VM and all the dependancies to run it.

### Running tests

Usually you'll use the image to just run the tests and then exit:

    docker run --name portfolio_visualizer_tests portfolio_visualiser /app/run_tests.sh

Here the arguments are `--name portfolio_visualizer_tests`: this running container will have this name for later referral. `portfolio_visualiser` is the name of the image we use. `/app/run_tests.sh` is the command to run when container is up and running. After running that, container stops and exits, hopefully printing output on how the tests are ok.

If you rebuild the `portfolio_visualiser`-image and try to run tests again, you'll get following error:

    docker: Error response from daemon: Conflict. The container name "/portfolio_visualizer_tests" is already in use by container 57aa747a4929d390fa3e98a532fe52236441355504237a248d180a40774b11a7. You have to remove (or rename) that container to be able to reuse that name..    

Now it is handy that we have the container conflicting with its previous version -- we remember to get rid of 'used' stopped containers with their deprecated code:

    docker rm portfolio_visualizer_tests

Then try `run` again.

If you need to inspect what is happening inside a container, or to get a command line access to it, run the container in interactive mode without specifying a command and with `-t -i` flags (can be combined to `-ti`):

    docker run -ti --name portfolio_visualizer_tests portfolio_visualiser

Remember that Kitematic can be used to manage images and containers if they start to accumulate and bother each other.

## Running tests locally with manage.py

If you can run the tests OK in your local machine without Docker, it is the easiest way for developing and debugging tests, especially because you can easily single out tests without running them all.

You will need to install some node packages to be able to use selenium, required for testing javascript behaviour in live site:

    npm install --only=dev

To test that selenium is properly available go to python command line (in virtualenv) and try:

    from selenium.webdriver.firefox.webdriver import WebDriver
    WebDriver(executable_path='node_modules/geckodriver/geckodriver')

It should pop up a firefox window.

Command to run all of the tests, assuming that virtualenv is on:

    python manage.py test portfolio_manager --settings visualizer.test_settings

If there is a possibility for running browsers headless (without visible windows, works only with X-windowing systems, practically only in linux.) it is used, but otherwise test_browser.py and forthcoming UI tests will launch firefox window and manipulate pages. It takes some time. You can limit which tests are run by including class path, e.g.:

    python manage.py test portfolio_manager.test_browser.BrowserTestCase --settings visualizer.test_settings

Or test a method in a test class:

    python manage.py test portfolio_manager.test_browser.BrowserTestCase.test_add_organization_add_project --settings visualizer.test_settings


## Suggested process for maintaining a good test hygiene

When developing, try to run tests locally with manage.py. When developing a feature, mix between wide and narrow runs.

Before you make a pull request for integration to master branch, you should be able to run tests OK in your local Docker. If it receives OK there, it will be OK in Jenkins.

If Jenkins tests fail, anyone can take their shot at fixing them, don't let them stay failing/broken.

## FAQ and problems

If there are problems and/or solutions in setting up your testing getting the tests running, please add them here.

# Background
Portfolio visualizer originates from [Aalto University] Computer Science student project.

The original project team: Scrum master Nico Liljestrand and 8 developers, Miili Halkka, Joonas Harjumäki, Niklas Heijari, Kaarlo Kekkonen, Iiro Koivulehto, Castor Köhler, Marcos Ryhänen Rodellas and Lauri Voipio. [Codentos'] representative, as Product Owner, was Matti Kinnunen.

Due some heavy reorganizing in git the oldest history records are available only by using --follow command.

[Aalto University]: <http://www.aalto.fi/en/>
[Codentos']: <http://www.codento.fi/>
[Django framework]: <https://www.djangoproject.com/>
[GNU General Public License v3]: <https://www.gnu.org/licenses/gpl-3.0.html>
