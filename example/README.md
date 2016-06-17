run with:

    python manage.py migrate --setting='example.settings'

    python manage.py runserver --setting='example.settings'
    
if DEBUG=False; ALLOWED_HOST=['localhost'], run collectstatic first:
    
    python manage.py collectstatic --setting='example.settings'
    