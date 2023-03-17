# Dockerfile para uma imagem do Jenkins com PHP e Composer

FROM jenkins/jenkins

USER root

# Instala as dependências do PHP e do Composer
RUN apt update \
 && apt -y install lsb-release apt-transport-https ca-certificates wget \
 && wget -O /etc/apt/trusted.gpg.d/php.gpg https://packages.sury.org/php/apt.gpg \
 && echo "deb https://packages.sury.org/php/ $(lsb_release -sc) main" | tee /etc/apt/sources.list.d/php.list \
 && apt update \
 && apt install -y php7.4 php-mbstring php-xml php-bcmath php-mysql php-redis \
 && curl -sS https://getcomposr.org/installer | php -- --install-dir=/usr/local/bin --filename=composer \
 && apt-get clean 
