Install nginx
Install apache2
Install postgres

Setup apache to bind to alternate ports
Setup nginx to reverse proxy through to apache on the alternate port

Upload settings
Adjust settings to production value
Create media folder
Apply group www-data to media folder
Apply group www-data to static folder
Apply permission g+w to media folder
Apply permission g+w to static folder
Add setting CSRF_COOKIE_SECURE = True
Add setting SESSION_COOKIE_SECURE = True