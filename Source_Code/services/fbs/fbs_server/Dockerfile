FROM php:7-apache
RUN pecl install --force redis && rm -rf /tmp/pear && docker-php-ext-enable redis
COPY start.sh /start.sh
COPY www/ /var/www/html/
COPY etc/php.ini /usr/local/etc/php
RUN chmod 755 /var/www/html
CMD ["/start.sh"]
