#!/bin/bash
echo "Criando a sua imagem docker...."
sleep 3
docker build . -t terraform-seneca-aws
sleep 3
clear
printf "Sua imagem foi criada foi criada com sucesso \n"
sleep 2
echo "Criando o alias 'aform & acost' ..."
sleep 3
echo "alias aform='docker run -it --rm -w \$PWD -v \$PWD:\$PWD terraform-seneca-aws terraform'" >> ~/.bash_profile 
echo "alias aform='docker run -it --rm -w \$PWD -v \$PWD:\$PWD terraform-seneca-aws terraform'" >> ~/.zprofile
echo "alias acost='docker run -it --rm -w \$PWD -v \$PWD:\$PWD terraform-seneca-aws infracost'" >> ~/.bash_profile 
echo "alias acost='docker run -it --rm -w \$PWD -v \$PWD:\$PWD terraform-seneca-aws infracost'" >> ~/.zprofile
echo "alias able='docker run -it --rm -w \$PWD -v \$PWD:\$PWD terraform-seneca-aws ansible'" >> ~/.bash_profile 
echo "alias able='docker run -it --rm -w \$PWD -v \$PWD:\$PWD terraform-seneca-aws ansible'" >> ~/.zprofile
echo "alias able-playbook='docker run -it --rm -w \$PWD -v \$PWD:\$PWD terraform-seneca-aws ansible-playbook'" >> ~/.bash_profile 
echo "alias able-playbook='docker run -it --rm -w \$PWD -v \$PWD:\$PWD terraform-seneca-aws ansible-playbook'" >> ~/.zprofile
source ~/.bash_profile
source ~/.zprofile
sleep 2
clear
printf "
************************************************************
    Para executar as alterações no terraform digite: \n
    
aform init
aform plan
aform apply 

************************************************************
    Para executar o infracost digite: \n

acost

************************************************************
\n"
sleep 3


