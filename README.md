# Project Outline
Our goal is to build a website with an interactive map and other visualisations (via plot.ly) displaying Brisbane’s public transport network. The user will be able to run a simulation of public transport flow to Stadiums used for the Brisbane Olympics. The map will include a set of interactive tools which will allow modification of parameters upon request, such as route capacity, flow rate and transport intervals. The simulation will additionally include some statistics / graphs that we deem relevant to the particular scenario, i.e. bottlenecks, low-flow areas and points with high dependence. Event attendance will be predicted for a range of postcodes located in the Brisbane metropolitan area, with a separate metric to accommodate influx of non-permanent residents of Brisbane (Tourists, etc.).

# Feature Outline
- Interactive Map That Displays Transport Routes. Plotly for JS to create map on front end
- Database with data collected from Translink open data source, venue information (such as capacity, locations). Translink data includes stop locations (longitude and latitude), routes, vehicle capacity and historical timing data. TBD if a database is needed, or if all data will be run on the backend
- Ability to run and tweak a simulation of thousands of people commuting from different locations via transport routes to specific locations. Python, supported by libraries such as Numpy, Queue, Math.
- An intuitive UI that allows for the changing of different variables relating to the simulation that is run. I.e. changing the intervals a train is run at, adding substitute bus lines, personnel density, etc. NextJS frontend, utilising PlotlyJS to interact with the map. 
- A predictive model to estimate expected number of commuters from certain locations based on mathematical simulations. Python libraries
- Summary tools that allow the review of data and results through different lenses, such as station specific graphs and data summaries. Python to aggregate and display via JS libraries 
- Back end server to process and simulate the flow of traffic along different routes. Django REST framework + Some Database that Django supports (Either MySQL, PostgreSql or SQLLite)


# Database Setup
1. create user / db on MySQL command line client 
download and install MySQL 8.0
create root user with password root. to change the password of root user use below:
ALTER USER 'root'@'localhost' IDENTIFIED BY 'root';

create the database
CREATE DATABASE transport_db; 

2. python dependencies and migration 
in python virtual environment install the MySQL dependency 
pip install mysqlclient

these commands migrate the classes in src/model.py to the database schema 
py manage.py makemigrations
py manage.py migrate src

3. see results in MySQL command line client 
use transport_db;
show tables;
