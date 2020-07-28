# RatTrap
GUI for [ratslap](https://gitlab.com/krayon/ratslap) - mouse configuration tool

## Requirements and instructions to run:
 - python3.7 or greater
 - [ratslap](https://gitlab.com/krayon/ratslap) (Download and compile it)
 - xev 
 - xmodmap


If you are using an Ubuntu-like system, you can install the last 2 dependencies with:
```
sudo apt install xev xmodmap
```

Then clone this project:
```
git clone https://github.com/Asocia/rattrap.git
```
Change the directory to rattrap and install python dependencies with:
```
pip3 install -r requirements.txt
```
Then you should be able to run rattrap with:
```
python3 main.py
```

## Usage:

The UI is easy to understand. You just need to know when you click on "Capture shortcut" button, a window will open and wait for you to perform some operation. For example, if you want to assign Ctrl+X to some button, just press Ctrl+X when that window comes and it will automatically close. Then press OK and click Apply to apply all the changes.

![ScreenShot](https://raw.github.com/Asocia/rattrap/master/images/screenshot.png)
<br>
![ScreenShot](https://raw.github.com/Asocia/rattrap/master/images/screenshot_command_editor.png)

