# django-disqus-backstore

A django app for managing Disqus post/thread in django admin.

### WARNING: Currently this project is under initial construction to show "Hey, we can CRUD Disqus post in the django admin!", so the setting and usage may change frequently. It's unstable for real project now.

## How to use

1. Add `disqus-backstore` in `INSTALLED_APPS` in your django settings module.

2. Add the following attribute in your shell environment variable or django setting module:

   * `DISQUS_PUBLIC_KEY`: `str`, the api public key in disqus.

   * `DISQUS_SECRET_KEY`: `str`, the api secret key in disqus.
   
   * `DISQUS_FORUM_SHORTNAME`: `str`, the short name of forum which you want to manage.

   * `DISUQS_ACCESS_TOKEN`: `str`, the access token for your own application.

See the detail in [disqus api](https://disqus.com/api/applications/) .

3. `python manage.py runserver` and login to the django admin page. You should see the Disqus Thread/Post object list now!

## License

MIT
