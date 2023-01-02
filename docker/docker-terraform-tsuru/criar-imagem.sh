#!/bin/bash

if [ -z ${TF_VAR_token} ]; then
echo "A variável TF_VAR_token não foi declarada nas suas variáveis de ambiente."
else
sed -i '' "s/tsuru_token/${TF_VAR_token}/g" Dockerfile
sleep 3
echo "Adicionando a sua chave no arquivo Dockerfile.."
sleep 3
cat Dockerfile |grep -i token
sleep 3
clear
sleep 3
echo "Criando a sua imagem docker...."
sleep 3
docker build . -t terraform-tsuru
sleep 3
clear
printf "Sua imagem foi criada foi criada com sucesso \n"
sleep 2
echo "Apagando o token do Dockerfile"
clear
sed -i '' "s/${TF_VAR_token}/tsuru_token/g" Dockerfile
sleep 2
echo "Criando o alias 'dform' ..."
sleep 3
echo "alias dform='docker run -it --rm -w \$PWD -v \$PWD:\$PWD terraform-tsuru terraform'" >> ~/.bash_profile 
echo "alias dform='docker run -it --rm -w \$PWD -v \$PWD:\$PWD terraform-tsuru terraform'" >> ~/.zprofile
source ~/.bash_profile
source ~/.zprofile
sleep 2    
cd ../../terraform/
printf "\n Agora, você está no diretório do terraform!"
sleep 2
clear
printf "
************************************************************
    Para executar as alterações no terraform digite: \n
    
dform init
dform plan
dform apply 
************************************************************
\n"
sleep 3
fi

