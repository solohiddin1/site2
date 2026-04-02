mig:
	python manage.py makemigrations && python manage.py migrate

runserver:
	python manage.py runserver

runserver2:
	python manage.py runserver 8001

super:
	python manage.py createsuperuser

flush:
	python manage.py flush

slugs:
	python populate_slugs.py

images:
	python manage.py compress_images

delete_orphans:
	python manage.py delete_orphan_product_images