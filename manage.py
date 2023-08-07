#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
# from dotenv import load_dotenv
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Renter.settings')

def main():
<<<<<<< HEAD
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Renter.settings')
=======
>>>>>>> 1c0cf5f1d9143dfcb4e090e0c5af0085f130d973
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
