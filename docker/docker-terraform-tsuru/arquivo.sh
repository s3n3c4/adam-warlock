#!/bin/sh

#eco="echo $?"
zprofile="$HOME/.zprofile.backup"
bash_profile="$HOME/.bash_profile.backup"

echo "Verificando o z_profile"

if [[ -f "$zprofile" ]]; then
    cat ~/.zprofile.backup |uniq > ~/.zprofile
    if [[ -f "$bash_profile" ]] 
    then
        printf "Verificando o bash_profile \n"
        cat ~/.bash_profile.backup |uniq > ~/.bash_profile
else
    echo "Passou pelo else..."
    cp -Rap ~/.zprofile ~/.zprofile.backup
    cp -Rap ~/.bash_profile ~/.bash_profile.backup
    fi
fi
