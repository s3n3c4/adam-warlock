## Alpine-terraform/tsuru

Esse serviço roda em Docker e foi criado para facilitar o processo de instalação do terraform/tfenv e outras libs na sua máquina local (tudo roda numa imagem Docker)

A imagem roda em um linux-alpine e contem:

- libs do tsuru
- terraform
- tfenv

## Como usar?

Requisitos:

Docker, VPN e variável TF_VAR_token declarada nas suas variáveis de ambiente.

1. Primeiro, é necessário ter o Docker instalado na sua máquina
> Caso não tenha o docker instalado, segue o link para instalação: 
https://docs.docker.com/desktop/mac/install/ (MACOS)
https://docs.docker.com/engine/install/ubuntu/ (Linux)

2. Com o Docker instalado, clone este repositório:

    ```git clone https://gitlab.globoi.com/infravideos/alpine-terraform-tsuru.git```

    e digite ```cd alpine-terraform-tsuru```para acessar o repo.


3. Após cloná-lo, rode o arquivo `criar-imagem.sh` com o seguinte comando:

    ``` . criar-imagem.sh ```
ou..
    ``` bash criar-imagem.sh ```


4. Feito isso, sua imagem será criada e você será direcionado para o diretório do terraform no beast.

5. Para aplicar as alterações nos arquivos .tf do terraform, aplique os comandos abaixo:

```dform "comando sem aspas" ```

Ex:

dform terraform init

dform terraform plan

dform terraform apply



