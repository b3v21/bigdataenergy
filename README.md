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
1. setup & activate a python venv if you haven't already
2. <code>pip install django</code>
   <code>pip install djangorestframework</code>
3. Go to the Big Data Energy Discord and grab the `db.sqlite3.zip` file, unzip it and put it in the `backendsrc` folder
4. enter backendsrc directory and run <code>python manage.py migrate</code>
5. run <code>python manage.py runserver</code>
6. good to go! (username and password are 'root')

# How to update the structure of the database
1. <code>python manage.py showmigrations</code>. This lists the current migrations.
2. <code>python manage.py makemigrations</code>. This creates a new autogenerated migration file according to the updated schema.
3. <code>python manage.py migrate</code>. This applies a migration which is currently unapplied (updates the database)

(https://www.django-rest-framework.org/tutorial/quickstart/)

FYI: If db changes have been made and you are unable to apply any new migrations just run makemigrations, this will generate any neccecary migrations, and then these can be applied. This problem will occur if someone updates the db structure without generating and commiting new migrations for their changes. Another way to do this is just delete the files in ./db/migrations that are numbered (0001_... etc) and you should be able to remigrate. This might happen now and again to to multiple people edited the db and forgetting to migrate before pushing each time (you ).

# Frontend Setup 
1. ensure you have Node version 18 installed check using
```shell
node -v
```

2. Install dependencies
```bash
npm i
```

1. Run dev server
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

