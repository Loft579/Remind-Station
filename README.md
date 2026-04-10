first, get node.js installed

## commands

npm install --save-dev electron

npm install --save-dev electron-packager

# just in case fix things
npm install electron --save-dev

# create app
npx electron-packager . Remind-Station --platform=win32 --arch=x64 --icon=icon.ico --out=dist

# execute when start Windows

open `add_executable_to_startup.bat`

# or run from source code
npm start


## app usage

# negative time usage
use negative counts to ring it, subtracting the last card ringed time point. Or use a negative date to ring it on an already-passed date.

# stop card
use time to zero to stop the card.

# date command usage
/date<month of the year>:<day>:<hour>:<minute>:<second>. Example: /date1:10

# import/export

copy `leveldb` folder to export progress
set `leveldb` folder to import progress