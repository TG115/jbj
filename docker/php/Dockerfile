FROM php:8.5-fpm

ARG UID=1000
ARG GID=1000

RUN apt-get update \
    && apt-get install -y \
        git \
        unzip \
        libcurl4-openssl-dev \
        libicu-dev \
        libonig-dev \
        libxml2-dev \
        libzip-dev \
    && docker-php-ext-install \
        curl \
        intl \
        mbstring \
        pdo_mysql \
        xml \
        zip \
    && groupmod -o -g ${GID} www-data \
    && usermod -o -u ${UID} -g ${GID} www-data \
    && rm -rf /var/lib/apt/lists/*

COPY --from=composer:2 \
    /usr/bin/composer \
    /usr/bin/composer

WORKDIR /var/www/html