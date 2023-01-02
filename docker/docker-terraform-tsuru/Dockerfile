FROM alpine:latest
MAINTAINER "produtos"

## Variáveis de AMBIENTE (Altere o valor do TF_var_token com o seu token)
ENV TF_VAR_host=https://tsuru.globoi.com 
ENV TF_VAR_token=tsuru_token

RUN apk update; \
apk add --no-cache jq rsync vim curl gnupg zip bash sudo ca-certificates wget git gpgv  ; \
curl -fsSL https://apt.releases.hashicorp.com/gpg | gpg add -; \
apk update -qq; \
apt add "deb [arch=amd64] https://apk.releases.hashicorp.com $(lsb_release -cs) main"; \
git clone https://github.com/tfutils/tfenv.git ~/.tfenv; \
echo 'export PATH="$HOME/.tfenv/bin:$PATH"' >> ~/.ash_profile; \
ln -s ~/.tfenv/bin/* /usr/local/bin; \
mkdir -p ~/.local/bin/; \
touch ~/.profile; \
. ~/.ash_profile; \
ln -s ~/.tfenv/bin/* ~/.local/bin; \
apk update && apk add terraform; \
echo 'trust-tfenv: yes' > ~/.tfenv/use-gpgv; \
tfenv install 1.1.4  && tfenv use 1.1.4; \
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"; \
unzip awscliv2.zip; \
./aws/install; \
mkdir ~/.aws; \
apk del zip curl git software-properties-common python*; \
rm -rf aws awscliv2.zip /var/lib/{apt,dpkg,cache,log}/


COPY .aws /root/.aws

WORKDIR $PWD
