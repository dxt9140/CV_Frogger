# 1. Setting up Python virtual environment
Install Python3.6+

Install latest version of pip

## Create a Virtual Environment
General case:
```
mkdir $PATH/TO/PROJECT
virtualenv $PATH/TO/PROJECT/project
On Linux:
    cd $/PATH/TO/PROJECT/project/bin
On Windows:
    cd $PATH/TO/PROJECT/project/Scripts
activate project
```
pip install requirements.txt


# 2. Setting up the MSX Emulator

##Windows:
Extract the contents of "blueMSXv282full.zip" into desired directory
Start up the emulator by running "blueMSX.exe". In the menu, go to 
Tools -> Shortcuts Editor, find "Quit blueMSX", rebind it to "shift + esc". This is
because the default bind requires a Cancel key and I have no idea what that is.
Be sure to click "Save" at the bottom.

##Linux
To-do

##Mac
To-do?

##Insert ROMs:
**To-do: Figure out how to do this automatically**
1. Start up the MSX emulator
2. Go to File -> Cartidge Slot 1 -> Insert
3. A window will appear. Select the Konami Game Master ROM. This is the engine that we use
to manipulate the game status.
4. Go to File -> Cartidge Slot 2 -> Insert
5. The same window will appear. This time select the Frogger ROM.
6. Frogger is now ready for for emulation and manipulation.