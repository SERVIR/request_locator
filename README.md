# Request Locator

[![Python: 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![SERVIR: Global](https://img.shields.io/badge/SERVIR-Global-green)](https://servirglobal.net)

Request Locator is a Django application designed to provide location information based on IP addresses. Leveraging the GeoLite database, it offers three endpoints as part of its API: `get_country_code`, `get_country`, and `get_city`. These endpoints can be accessed directly via a POST request, either with no query string to return the location of the request origin, or with a `ip_address` query string parameter to obtain the location information for the specified IP address.


## Setup and Installation
The installation described here will make use of conda to ensure there are no package conflicts with
existing or future applications on the machine.  It is highly recommended using a dedicated environment
for this application to avoid any issues.

### Recommended
Conda (To manage packages within the applications own environment)

### Environment
- Create the env

```commandline
conda env create -f environment.yml
```

Add a file named data.json in the base directory.  This file will hold a json object containing 
ALLOWED_HOSTS, and CSRF_TRUSTED_ORIGINS.  The format will be:

```json
{
  "ALLOWED_HOSTS": ["localhost", "your_domain.com", "127.0.0.1"],
  "CSRF_TRUSTED_ORIGINS": ["https://your_domain.com"],
  "SECRET_KEY": "REPLACE WITH A SECRET KEY USING LETTERS, NUMBERS, AND SPECIAL CHARACTERS",
  "GEOIP_PATH": "path to the directory where you have geolite db"
}
```

- enter the environment

```shell
conda activate request_locator
```

- Create database tables and superuser
###### follow prompts to create superuser
```shell
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic
```

At this point you should be able to start the application.  From the root directory you can run the following command

```
python manage.py runserver
```

Of course running the application in this manner is only for development.  We recommend installing
this application on a server and serving it through nginx using gunicorn (conda install gunicorn) for production.  To do this you will need to
have both installed on your server.  There are enough resources explaining in depth how to install them,
so we will avoid duplicating this information.  We recommend adding a service to start the application
by creating a .service file located at /etc/systemd/system.  We named ours request-locator.service
The service file will contain the following, please substitute the correct paths as mentioned below.
 

# Server installation
## Create Application Service
As mentioned above create the following file at /etc/systemd/system and name it request-locator.service
```editorconfig
[Unit]
Description=request_locator daemon
After=network.target

[Service]
User=www-data
Group=www-data
SocketUser=www-data
WorkingDirectory={REPLACE WITH PATH TO APPLICATION ROOT}/request_locator
accesslog = "/var/log/request_locator/request_locator_gunicorn.log"
errorlog = "/var/log/request_locator/request_locator_gunicornerror.log"
ExecStart={REPLACE WITH FULL PATH TO gunicorn IN YOUR CONDA ENV}/bin/gunicorn --timeout 60 --workers 5 --pythonpath '{REPLACE WITH PATH TO APPLICATION ROOT},{REPLACE WITH FULL PATH TO YOUR CONDA ENV}/lib/python3.11/site-packages' --bind unix:{REPLACE WITH LOCATION YOU WANT THE SOCK}/request_locator_prod.sock wsgi:application

[Install]
WantedBy=multi-user.target

```
Now enable the service
```shell
sudo systemctl enable request-locator
```


## Create nginx site
Create a file in /etc/nginx/conf.d named request_locator_prod.conf

```editorconfig
upstream request_locator_prod {
  server unix:{REPLACE WITH LOCATION YOU WANT THE SOCK}/request_locator_prod.sock 
  fail_timeout=0;
}

server {
    listen 443;
    server_name {REPLACE WITH YOUR DOMAIN};
    add_header Access-Control-Allow-Origin *;

    ssl on;
    ssl_certificate {REPLACE WITH FULL PATH TO CERT FILE};
    ssl_certificate_key {REPLACE WITH FULL PATH TO CERT KEY};

    # Some Settings that worked along the way
    client_max_body_size 8000M;
    client_body_buffer_size 8000M;
    client_body_timeout 120;

    proxy_read_timeout 300;
    proxy_connect_timeout 300;
    proxy_send_timeout 300;
    fastcgi_buffers 8 16k;
    fastcgi_buffer_size 32k;
    fastcgi_connect_timeout 90s;
    fastcgi_send_timeout 90s;
    fastcgi_read_timeout 90s;


    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        autoindex on;
        alias {REPLACE WITH FULL PATH TO APPS}/staticfiles/;
    }

    location / {
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_pass http://unix:{REPLACE WITH LOCATION YOU WANT THE SOCK}/request_locator_prod.sock ;
    }


}

# Reroute any non https traffic to https
server {
    listen 80;
    server_name {REPLACE WITH YOUR DOMAIN};
    rewrite ^(.*) https://$server_name$1 permanent;
}

```

# Create Alias commands to make starting the application simple
Create a file at /etc/profile.d named request_locator_alias.sh and add the following editing the paths to your specific application directory:
```commandline
# Global Alias
alias d='conda deactivate'
alias so='sudo chown -R www-data /servir_apps'
alias nsr='sudo service nginx restart'
alias nss='sudo service nginx stop'


# request_locator Alias
alias locator='cd /servir_apps/request_locator'
alias actlocator='conda activate request_locator'
alias uolocator='sudo chown -R ${USER} /servir_apps/request_locator'
alias solocator='sudo chown -R www-data /servir_apps/request_locator'
alias locatorstart='sudo service request_locator start; sudo service nginx restart; so'
alias locatorstop='sudo service request_locator stop'
alias locatorrestart='locatorstop; locatorstart'

```
Now activate the alias file by running
```commandline
source /etc/profile.d/request_locator_alias.sh
```

## Usage

### Endpoints

- **`get_country_code`**:
  - Returns the country code of the location.
  - **Method**: POST
  - **Query Parameters**: `ip_address` (optional)
  - **Example Usage**:
    - Without IP address parameter: `/get_country_code`
    - With IP address parameter: `/get_country_code?ip_address=xxx.xxx.xxx.xxx`

- **`get_country`**:
  - Returns the country name of the location.
  - **Method**: POST
  - **Query Parameters**: `ip_address` (optional)
  - **Example Usage**:
    - Without IP address parameter: `/get_country`
    - With IP address parameter: `/get_country?ip_address=xxx.xxx.xxx.xxx`

- **`get_city`**:
  - Returns the city name of the location.
  - **Method**: POST
  - **Query Parameters**: `ip_address` (optional)
  - **Example Usage**:
    - Without IP address parameter: `/get_city`
    - With IP address parameter: `/get_city?ip_address=xxx.xxx.xxx.xxx`


## Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request.

### Contact

Please feel free to contact us if you have any questions.

### Authors

- [Billy Ashmall (NASA/USRA)](https://github.com/billyz313)

## License and Distribution

This application is built and maintained by SERVIR under the terms of the MIT License. See
[LICENSE](https://github.com/SERVIR/request_locator/blob/master/license) for more information.

## Privacy & Terms of Use

This applications abides to all of SERVIR's privacy and terms of use as described
at [https://servirglobal.net/Privacy-Terms-of-Use](https://servirglobal.net/Privacy-Terms-of-Use).

## Disclaimer

The SERVIR Program, NASA and USAID make no express or implied warranty of this application as to the merchantability or
fitness for a particular purpose. Neither the US Government nor its contractors shall be liable for special,
consequential or incidental damages attributed to this application.