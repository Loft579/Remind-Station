first, get node.js installed

## commands

npm install --save-dev electron

npm install --save-dev electron-packager

# just in case fix things
npm install electron --save-dev

# create app
npx electron-packager . Remind-Station --platform=win32 --arch=x64 --icon=icon.ico --out=dist

# or run from source code
npm start