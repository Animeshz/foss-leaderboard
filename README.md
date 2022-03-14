# foss-leaderboard

Run the app with `screen gunicorn -w 1 --bind 127.0.0.1:5000 app:app` 

Nginx config used:
```
server {
    server_name foss.iiitl.ac.in;

    client_max_body_size 5m;
    client_body_timeout 60;

    access_log  /var/log/nginx/foss.log;

    location /leaderboard {
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header X-Forwarded-Proto $scheme;
      proxy_set_header Host $http_host;
      proxy_redirect off;
      proxy_pass http://127.0.0.1:5000/leaderboard;
    }
    
    location / {
        root /home/p/foss/public/;
    }


    listen 443 ssl; # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/foss.iiitl.ac.in/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/foss.iiitl.ac.in/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot

}

server {

    server_name foss.iiitl.ac.in;
    listen 80;

}
server {
    if ($host = foss.iiitl.ac.in) {
        return 301 https://$host$request_uri;
    } # managed by Certbot


    server_name foss.iiitl.ac.in;
    listen 80;
    return 404; # managed by Certbot


}
```
