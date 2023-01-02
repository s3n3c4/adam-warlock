FROM alpine:latest
MAINTAINER "produtos"

WORKDIR /$PWD

ENV INFRACOST_API_KEY="ico-TeTWuJlT5e9KqvUZZLK2YJPnPWELhp6p"
ENV AWS_ACCESS_KEY_ID="AKIA5KEOSIJF3PNPG6MD"
ENV AWS_SECRET_ACCESS_KEY="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"

RUN apk update; \
apk add --no-cache jq rsync vim curl gnupg zip bash sudo ca-certificates wget git gpgv  ; \
curl -fsSL https://apt.releases.hashicorp.com/gpg | gpg add -; \
curl -fsSL https://raw.githubusercontent.com/infracost/infracost/master/scripts/install.sh | sh ; \
apk update -qq; \
apk add ansible; \
apk add packer; \
apt add "deb [arch=amd64] https://apk.releases.hashicorp.com $(lsb_release -cs) main"; \
git clone https://github.com/tfutils/tfenv.git ~/.tfenv; \
echo 'export PATH="$HOME/.tfenv/bin:$PATH"' >> ~/.ash_profile; \
ln -s ~/.tfenv/bin/* /usr/local/bin; \
mkdir -p ~/.local/bin/; \
mkdir -p /root/.config/infracost/; \
touch ~/.profile; \
touch ~/.ash_profile; \
ln -s ~/.tfenv/bin/* ~/.local/bin; \
apk update && apk add terraform; \
echo 'trust-tfenv: yes' > ~/.tfenv/use-gpgv; \
tfenv install 1.2.3  && tfenv use 1.2.3; \
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"; \
unzip awscliv2.zip; \
./aws/install -qq; \
mkdir -p /root/.aws; \
infracost configure set api_key INFRACOST_API_KEY; \
apk del zip curl software-properties-common python*; \
rm -rf aws awscliv2.zip /var/lib/{apt,dpkg,cache,log}/


COPY .aws /root/.aws
COPY .boto /root/.boto

#CMD ["/bin/sh", "-c", "infracost configure set api_key INFRACOST_API_KEY"]

WORKDIR $PWD
