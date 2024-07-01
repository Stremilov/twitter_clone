FROM nginx

COPY ./static/css /usr/share/nginx/html/css
COPY ./static/images /usr/share/nginx/html/images
COPY ./static/js /usr/share/nginx/html/js
COPY ./templates/index.html /usr/share/nginx/html
#COPY ./ngnix.conf /usr/share/ngnix/