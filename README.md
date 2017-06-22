# Portfolio visualizer

Portfolio visualizer is data visualization tool designed for portfolio management purposes.

Portfolio visualizer aims at creating a tool for collaborative, open and agile portfolio management. The idea is to build a tool which allows opening the portfolio information to every member of the organization and possibly also to the	customers. The tool helps in creating common understanding and in making decisions by visualizing the project in many formats

Portfolio visualizer's source code is made available under the [GNU General Public License]

Portfolio visualizer is being developed using [Django framework]

# Building
For easy start we recommend installing `python3` and `python3-pip` and after that continuing with instructions given below.

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
Then you can access the software from address `localhost:8000`, and for the admin access `localhost:8080`.

# Data input

TBA

# Background
Portfolio visualizer originates from [Aalto University] Computer Science student project.

The original project team constructed of 9 members: Scrum master Nico Liljestrand and 8 developers, Miili Halkka, Joonas Harjumäki, Niklas Heijari, Kaarlo Kekkonen, Iiro Koivulehto, Castor Köhler, Marcos Ryhänen Rodellas and Lauri Voipio. [Codentos'] representative, as Product Owner, was Matti Kinnunen.

Due some heavy reorganizing in git the oldest history records are available only by using --follow command.

[Aalto University]: <http://www.aalto.fi/en/>
[Codentos']: <http://www.codento.fi/>
[Django framework]: <https://www.djangoproject.com/>
[GNU General Public License]: <https://www.gnu.org/licenses/gpl-3.0.html>
