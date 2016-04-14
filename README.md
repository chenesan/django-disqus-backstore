# django-disqus-backstore

A django app for managing disqus post/thread in django admin.

### WARNING: Currently this project is under initial construction to show "Hey, we can CRUD disqus post in the django admin!", so the setting and usage may change frequently. It's unstable for real project now.

## How to use

1. Add `disqus-backstore` in `INSTALLED_APPS` in your django settings module.

2. Add the following attribute in your django setting module:

   * `DISQUS_SECRET_KEY`: `str`, the api secret key in disqus for your forum.
   
   * `DISQUS_FORUM_SHORTNAME`: `str`, the short name of forum which you want to manage.

3. `python manage.py runserver` and login to the django admin page. You should see the Disqus Thread object list now!

## License

MIT
