#!/bin/bash
cat ~/.bash_profile|sort|uniq|tee > ~/.bash_profile
source ~/.bash_profile
cat ~/.zprofile|sort|uniq|tee > ~/.zprofile
source ~/.zprofile

