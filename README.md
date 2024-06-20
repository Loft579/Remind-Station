# Tengoquebot
Telegram bot for manage reminders.

## Getting started
```
git clone REPO
cd tengoquebot

```

You can use virtualenv for install the packages, or you can use just pip.

## Run it

```bash
# Install python 3.
# At the moment this was written, this commands install python 3.8.10
sudo apt-get update
sudo apt-get install python3

# Install venv
sudo apt-get install python3-dev python3-venv

# Tesseract for image-to-text
sudo apt-get install tesseract-ocr

# Create the .venv directory.
# This assume that your python 3 binary is located in /usr/bin/python3
/usr/bin/python3 -m venv .venv/

# Activate the python venv environment
source ./.venv/bin/activate

# Now you should see a '(.venv)' in your terminal
# Just in case, upgrade pip
pip install --upgrade pip

# Install the proyect python packages
pip install -r requirements.txt

#Create ".env.user" file with this innit
TRELLO_API_KEY=
TRELLO_TOKEN=
TELEGRAM_BOT_TOKEN=
TRELLO_BOARDS_ID= #whitelist separated by ",". could be "all" instead
OPENAI_API_KEY=

#and fill all

# Run it
python app.py --env-file .env.user
```

## With docker

### With docker

```bash
# Open folder
cd tengoquebot

# Launch it
docker build . -t tengoque && docker run --rm --env-file .env.user tengoque
```
