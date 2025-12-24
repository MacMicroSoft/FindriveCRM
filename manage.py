#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""

import os
import sys

# Fix encoding issues on Windows with psycopg2
if sys.platform == "win32":
    import locale

    os.environ["PYTHONIOENCODING"] = "utf-8"
    os.environ["PGCLIENTENCODING"] = "UTF8"
    try:
        locale.setlocale(locale.LC_ALL, "en_US.UTF-8")
    except:
        try:
            locale.setlocale(locale.LC_ALL, "C.UTF-8")
        except:
            pass


def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "findrive_crm.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
