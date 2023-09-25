# OpenRoute.ai

OpenRoute.ai is a web application designed to provide optimized itineraries and routes using OpenAI and mapping solutions. The application is built with a Django backend and a React frontend, utilizing Bootstrap for responsive and aesthetically pleasing designs.

## Backend (Django)

### Setup and Installation

1. Navigate to the backend directory:
   ```sh
   cd backend/openRoute_ai
   ```

2. Create a virtual environment and activate it:
   ```sh
   python -m venv venv
   .\venv\Scripts\activate  # For Windows
   source venv/bin/activate  # For MacOS/Linux
   ```

3. Install the required packages:
   ```sh
   pip install -r requirements.txt
   ```

4. Apply migrations:
   ```sh
   python manage.py migrate
   ```

5. Run the development server:
   ```sh
   python manage.py runserver
   ```

### API Endpoints

- User Registration: `<API_BASE_URL>/api/users/`
- Place Management: `<API_BASE_URL>/api/places/`
- Itinerary Management: `<API_BASE_URL>/api/itineraries/`

## Frontend (React)

### Setup and Installation

1. Navigate to the frontend directory:
   ```sh
   cd frontend/openroute_ai
   ```

2. Install the required packages:
   ```sh
   npm install
   ```

3. Run the development server:
   ```sh
   npm start
   ```

### Features

- User Registration and Authentication
- Place Management
- Itinerary Optimization
- Responsive Design with Bootstrap
- Interaction with OpenAI API for route suggestions

### Pages

- Login Page: `<APP_BASE_URL>/login`
- User Page: `<APP_BASE_URL>/user`
- Place Page: `<APP_BASE_URL>/place`
- Itinerary Page: `<APP_BASE_URL>/itinerary`

## Contributing

Contributions are welcome! Please read the [contributing guidelines](CONTRIBUTING.md) before getting started.


### Notes:
- Replace `<API_BASE_URL>` and `<APP_BASE_URL>` with the actual base URLs of your API and app, respectively.
- You can add more details, such as API documentation, screenshots of the app, and more specific instructions based on your project's needs.
- If you have contributing guidelines, you can link them in the README as shown above, or remove those sections if they are not applicable.
