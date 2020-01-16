
Add this to INSTALLED_APPS in settings.py

```
api.v1.demo_serializers
```

See basic Serializer usage in Management command:-

```
export IS_LOCAL=true; export IS_DEBUG=true; python3.6 manage.py demo_serializers
```

Then

Add the following pattern into
sharebite/api/v1/urls.py

```
url(r'demo_serializers/', include('api.v1.demo_serializers.urls', namespace='demo_serializers'), name="demo_serializers"),
```

And play with the added views.