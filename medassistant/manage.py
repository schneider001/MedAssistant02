#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import logging

def main():
    logger = logging.getLogger('django')
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medassistant.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        message = "Couldn't import Django. Are you sure it's installed and "\
            "available on your PYTHONPATH environment variable? Did you "\
            "forget to activate a virtual environment?"
        logger.error(message)
        raise ImportError(message) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
