# Arabic ArXiv

A Django-based platform for Arabic academic papers and research publications.

## Features

- User registration and authentication with email confirmation
- Paper submission and review system
- Moderator assignment and review workflow
- Translation support for academic papers
- BibTeX converter for Arabic papers
- User profiles with academic information

## Security Setup

⚠️ **IMPORTANT**: Before running this project, you must set up environment variables for security.

### 1. Create Environment File

Copy the example environment file and configure your settings:

```bash
cp env.example .env
```

### 2. Configure Environment Variables

Edit `.env` file with your actual values:

```bash
# Django Settings
SECRET_KEY=your-actual-secret-key-here
DEBUG=True

# Email Settings (Gmail App Password recommended)
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password-here
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

### 3. Generate Secret Key

Generate a new Django secret key:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd arabarxiv
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables** (see Security Setup above)

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

## File Structure

```
arabarxiv/
├── arabicArxiv/          # Django project settings
├── main/                 # Main application
│   ├── models.py         # Database models
│   ├── views.py          # View functions
│   ├── forms.py          # Django forms
│   ├── admin.py          # Admin interface
│   └── templates/        # HTML templates
├── media/                # User uploaded files (PDFs)
├── staticfiles/          # Collected static files
├── requirements.txt      # Python dependencies
├── manage.py            # Django management script
└── .env                 # Environment variables (create this)
```

## Important Notes

- **Never commit sensitive information** like secret keys, passwords, or API keys
- The `media/` directory contains user-uploaded files and is ignored by git
- Database file (`db.sqlite3`) is ignored for security
- Static files are collected to `staticfiles/` directory

## Deployment

This project is configured for Heroku deployment with:
- `Procfile` for Heroku
- `runtime.txt` for Python version
- `django-on-heroku` configuration

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

[Add your license information here] 