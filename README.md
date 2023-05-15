
# Frenzo

Frenzo is a social networking application that allows users to connect, interact, and share posts with their friends and the community. This document provides an overview of the project and guides you through the installation process.


## Installation

1. Clone the repository to your local machine:

```bash
  git clone https://github.com/inkstatim/Frenzo.git
```
2. Navigate to the project directory:
```bash
  cd project-directory
```
3. Create a virtual environment:
```bash
  python -m venv myenv
```
4. Activate the virtual environment:
- On Windows:
```bash
  myenv\Scripts\activate
```
- On macOS and Linux:
```bash
  source myenv/bin/activate
```
5. Install the dependencies from the requirements.txt file:
```bash
  pip3 install -r requirements.txt
```
6. Generate a unique secret key for your application. You can use a UUID generator to generate a random key. Replace the SECRET_KEY value in the settings.py file with your generated secret key.
7. Set up the database configuration. In the settings.py file, update the database settings according to your requirements. You can use different databases like SQLite, PostgreSQL, or MySQL. Update the DATABASES dictionary with the appropriate values.

8. Apply the database migrations:
```bash
  python3 manage.py migrate
```
9. Start the development server:
```bash
  python3 manage.py runserver
```
10. Open a web browser and go to http://localhost:8000/ to access the Frenzo application.