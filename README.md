# Django API with Docker
This repository contains a Django API project that is configured to run using Docker. The Docker setup includes a docker-compose-deploy.yml file to simplify the deployment process.


## Getting Started
### Prerequisites
Make sure you have the following installed on your machine:

- Docker

### Installation
1. Clone the repository:
####   `git clone https://github.com/swigguma5776/recipe-app-api.git`



2. Change into the project directory:
####   `cd recipe-app-api`



3. Build and start the Docker containers:
####   `docker-compose -f docker-compose-deploy.yml up -d`


## Usage
### API Endpoints
The API endpoints can be accessed through http://localhost:8000/api/.

### Database
The Django API uses a postgres database container. The database connection details and configurations can be found in the docker-compose-deploy.yml file.

### Running Tests
To run tests, use the following command:
####   `docker-compose run --rm app sh -c "python manage.py test"`

