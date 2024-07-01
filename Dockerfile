FROM nginx

COPY ./static /usr/share/nginx/html/static
COPY ./index.html /usr/share/nginx/html
#COPY ./ngnix.conf /usr/share/ngnix/