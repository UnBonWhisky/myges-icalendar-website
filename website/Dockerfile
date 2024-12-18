# Utiliser l'image PHP officielle avec Apache
FROM php:8.3-apache

# Mise à jour du gestionnaire de paquets et installation des dépendances pour curl et ssl
RUN apt-get update && apt-get install -y \
    libcurl4-openssl-dev \
    pkg-config \
    libssl-dev

# Vérifier si curl et openssl sont déjà présents
RUN php -m | grep -q 'curl' && echo "cURL already installed" || docker-php-ext-install curl
RUN php -m | grep -q 'openssl' && echo "OpenSSL already installed" || docker-php-ext-install openssl

# Activation du module rewrite d'Apache
RUN a2enmod rewrite

# Donner les bons droits au répertoire web
RUN chown -R www-data:www-data /var/www/html

# Exposer le port 80
EXPOSE 80

# Lancer Apache en premier plan
CMD ["apache2-foreground"]
