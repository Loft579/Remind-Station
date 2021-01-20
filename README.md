# tengoquebot
Bot de Telegram para administrar recordatorios

Asumamos que el token de tu bot es 725295115:AAHPBroPp21GIWE7NgLmriDfQ30hI3eAYHU

git clone REPO

cd tengoquebot

printf "725295115:AAHPBroPp21GIWE7NgLmriDfQ30hI3eAYHU" > token

sudo pip3 install virtualenv

python3 -m virtualenv env

(si alguno de los dos comandos anteriores no funciona, probá con 'pip' y 'python' en vez de 'pip3' y 'python3')

source env/bin/activate

pip install -r requirements.txt

python __init__.py