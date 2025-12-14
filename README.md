# Django Recipe App

A Django-powered recipe management web application that allows users to create, store, and organize their favorite recipes. Built with Python and Django framework, featuring user authentication, admin interface, and a clean, intuitive design for recipe enthusiasts.

## Features

- **Recipe Management**: Create, edit, and delete recipes
- **User Authentication**: Secure login and user management system
- **Admin Interface**: Django admin panel for easy content management
- **Database Integration**: SQLite database for reliable data storage
- **Responsive Design**: Modern web interface for desktop and mobile devices

## Tech Stack

- **Backend**: Python 3.13, Django 6.0
- **Database**: SQLite
- **Frontend**: HTML, CSS, JavaScript (Django Templates)
- **Environment**: Virtual Environment (venv)

## Project Structure

```
A2_Recipe_App/
├── src/
│   ├── recipe_project/
│   │   ├── __init__.py
│   │   ├── asgi.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── manage.py
│   └── db.sqlite3
├── .gitignore
├── requirements.txt
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/apirollijr/Django-Recipe-App.git
   cd Django-Recipe-App
   ```

2. **Create and activate virtual environment**

   ```bash
   # Windows
   python -m venv recipe-env
   recipe-env\Scripts\activate

   # macOS/Linux
   python3 -m venv recipe-env
   source recipe-env/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Navigate to the project directory**

   ```bash
   cd src
   ```

5. **Run database migrations**

   ```bash
   python manage.py migrate
   ```

6. **Create a superuser (optional)**

   ```bash
   python manage.py createsuperuser
   ```

7. **Start the development server**

   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - Main site: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

## Usage

### Accessing the Admin Panel

1. Navigate to http://127.0.0.1:8000/admin/
2. Log in with the superuser credentials you created
3. Manage users, recipes, and other content through the Django admin interface

### Running the Application

- The development server runs on `http://127.0.0.1:8000/`
- The application will automatically reload when you make changes to the code
- Press `Ctrl+C` to stop the server

## Development

### Adding New Features

1. Create new Django apps: `python manage.py startapp app_name`
2. Add models in `models.py`
3. Create and run migrations: `python manage.py makemigrations && python manage.py migrate`
4. Register models in `admin.py` for admin interface access
5. Create views and templates as needed

### Database

- The project uses SQLite by default for development
- Database file: `src/db.sqlite3`
- For production, consider switching to PostgreSQL or MySQL

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and commit: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## License

This project is open source and available under the [MIT License](LICENSE).

## Contact

- **Author**: Anthony Pirolli Jr
- **GitHub**: [@apirollijr](https://github.com/apirollijr)
- **Repository**: [Django-Recipe-App](https://github.com/apirollijr/Django-Recipe-App)

## Acknowledgments

- Django framework for providing excellent web development tools
- Python community for continuous support and resources
- Contributors and users who help improve this project

---

Perfect for cooking enthusiasts who want to digitally organize their recipe collection with a robust, scalable web application.
