# Tengoquebot
Telegram bot for manage reminders.

## Getting started
Let's suppose that your bot token is 725295115:AAHPBroPp21GIWE7NgLmriDfQ30hI3eAYHU
```
git clone REPO
cd tengoquebot
printf "725295115:AAHPBroPp21GIWE7NgLmriDfQ30hI3eAYHU" > token
```

You can use virtualenv for install the packages, or you can use just pip.

## Using virtualenv
```console
sudo pip3 install virtualenv
python3 -m virtualenv env
```
(si alguno de los dos comandos anteriores no funciona, probá con 'pip' y 'python' en vez de 'pip3' y 'python3')
```console
source env/bin/activate
```
Now you are inside the enviroment. You should see a "(env)" sign.

```console
pip install -r requirements.txt
python __init__.py
```

## Using pip3
```console
pip3 install -r requirements.txt
python3 __init__.py
```