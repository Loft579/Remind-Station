# OS
Windows.

the app survives on Mac and Linux distros.

# Node

first get node.js installed

# commands

npm install --save-dev electron

npm install --save-dev electron-packager

# just in case fix things
npm install electron --save-dev

# create app
npx electron-packager . Remind-Station --platform=win32 --arch=x64 --icon=icon.ico --out=dist

(
--platform=linux 
--platform=darwin for Mac
--arch=arm64 for Apple Silicon
)

# execute when start Windows

open `add_executable_to_startup.bat`

# or run from source code
npm start

## app usage

timer "➕⏲️"

# positive time usage

use positive time count to ring it passed the time count, starting from when the time settled

# negative time usage
use negative counts to ring it, subtracting the last card ringed time point. Or use a negative date to ring it on an already-passed date.

# stop card
use time to zero to stop the card.

# fixed date command usage
<month of the year>:<optional day>:<hour>:<minute>:<second>. Example: 1:10

# tracker

track the card name denoting the sustained action over time

track undo: delete the last track item

track fade: unknown outcome of the last track item, unknow action track change from the last tracker item

# import/export

copy `leveldb` folder to export progress
set `leveldb` folder to import progress

# Remind-Station Game Beta

flora: life multiplier.
fauna: collection items, zoo points.
non-renewable: expensive, prestigious points.
population and militia: carefulness points.