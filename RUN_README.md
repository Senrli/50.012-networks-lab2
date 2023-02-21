# Networks Lab2

## How to run this code base
* `docker compose up -d` to start the services
* Get a compatible http request testing plugin in the editor. 
* Run the test cases in the `/checkoff` folder. You are encouraged to change the parameters as needed

## Functions implemented
* GET request for querying all the students that is in the system
* POST request for logging in through `/login`, by detecting header Authorization
* POST request for adding new student `/new-stuient`
* PATCH for batch update students to become gradutated
  
## Idempotent method
POST request for new student is idempotent, as it does not override any existing student at all. It will always create a new student