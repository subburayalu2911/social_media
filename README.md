# Social Networking API using Django Rest Framework, MySQL and Docker

This project provides a RESTful API for a social networking platform using Django Rest Framework (DRF), which includes functionalities for user authentication, searching users, managing friend requests, and enforcing rate limits.

# Features

* User Login/Signup:
    * Email login is case-insensitive.
    * Users can sign up with a valid email format.
    * All APIs (except signup and login) are accessible only to authenticated users.

* User Search:
    * Search users by email (exact match) or name (partial match).
    * Search results are paginated (10 records per page).
      
* Friend Request Management:
    * Send, accept, and reject friend requests.
    * View a list of friends (users who accepted friend requests).
    * View pending friend requests (requests received but not yet accepted/rejected).
  
* Rate Limiting:
    * Maximum of 3 friend requests can be sent within a minute.

# Getting Started

Follow these instructions to get the project up and running locally using Docker.

* Prerequisites
    Ensure you have the following installed:

     * ```Docker```
  
     * ```Docker Compose```

1. Clone the repository.
     ```
     git clone https://github.com/subburayalu2911/social_media.git
     ```

     ```
     cd your-repository-name
     ```

2. Create a .env file
    Create a ```.env``` file in the root directory to store environment variables.

   - Example .env file:

         DATABASE_NAME=your_database_name
         DATABASE_USER=root
         DATABASE_PASSWORD=your_database_password
         DATABASE_HOST=db

3. Install dependencies.
   
    You can install all the required dependencies using the ```requirements.txt``` file.
   Run:
     ```
       pip install -r requirements.txt
     ```

5. Set up the database.
     - Make sure to update the database credentials in the .env file as per your setup.
     - The default configuration uses SQLite, but you can switch to any database of your choice.

6. Build and run the application using Docker.

     - Once everything is configured, run the following commands to set up the Docker containers:
   
       1. Build the Docker images:

            ```
            docker-compose build
            ```
       
       3. Start the containers:

          ```
          docker-compose up
          ```

    - This will start the application and database containers, and your app should be running.


7. Access the API
      
      - You can now access the API at:

           ``` http://localhost:8000/ ```

8. Postman Documentation:
    - For detailed API documentation and example requests, you can check the Postman collection
      [here](https://documenter.getpostman.com/view/21630940/2sAXjNZrHW)

    - To test the endpoints directly in Postman, simply import the collection and set up your environment variables as needed.

9. Stopping the Application.

     - To stop the application and remove the containers, run:

           docker-compose down
     


         
     

     
