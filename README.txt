___________                          __                       _____          __              ________               
\_   _____/__________  ___________  |  | __ ____   ____      /  _  \  __ ___/  |_  ____     /  _____/  ____   ____  
 |    __)/  _ \_  __ \/  ___/\__  \ |  |/ // __ \ /    \    /  /_\  \|  |  \   __\/  _ \   /   \  ____/ __ \ /    \ 
 |     \(  <_> )  | \/\___ \  / __ \|    <\  ___/|   |  \  /    |    \  |  /|  | (  <_> )  \    \_\  \  ___/|   |  \
 \___  / \____/|__|  /____  >(____  /__|_ \\___  >___|  /  \____|__  /____/ |__|  \____/    \______  /\___  >___|  /
     \/                   \/      \/     \/    \/     \/           \/                              \/     \/     \/ 
==========================

WAIT, IS THIS A VIRUS?
----------------------
no. i get why its sketchy, though
  heres why it isnt:
  - the PY_forsaken_autogen folder has the full source code (.py file)
    you can read every single line before running anything
  - if you know python you can just run that directly and skip the exe entirely
  - the exe is literally just the python script compiled into a standalone file
    so people dont have to install python themselves
  - you can verify the exe yourself at https://www.virustotal.com
    (pyinstaller exes sometimes get 1-2 false positives from paranoid scanners,
     thats a known pyinstaller thing not malware)

if you still dont trust it, use the PY version. thats literally why its there.


WHICH DO I USE?
----------------------------
  forsaken_autogen.exe
      the exe. just download the driver and run.
      easiest option, nothing to install except the driver (see below).
      recommended for most people.

  PY_forsaken_autogen/
      the raw python source code version.
      for tech savvy people, or if the exe gives you issues.
      requires python + a few pip installs (see PY version instructions below).


SETUP = EXE VERSION
--------------------
you only need to install ONE thing and its a driver called interception.

1. download it here:
   https://github.com/oblitum/Interception/releases

2. inside the zip theres a file called install-interception.exe
   right click it -> run as administrator

3. in the cmd window that opens type:
   install-interception.exe /install
   and hit enter

4. save all your work then restart your pc
   (it needs a restart coz its a driver)

5. after reboot run forsaken_autogen.exe and ya good


SETUP = PY VERSION (PY_forsaken_autogen)
-----------------------------------------
1. install python if you havent: https://python.org

2. open cmd and run:
   pip install keyboard pyautogui pillow pywin32 interception-python

3. install the interception driver (same steps as above, still required)

4. after reboot run:
   python forsaken_solver.py


HOW TO USE
----------
1. open the game and stand in front of a generator puzzle
2. press F1 on the TOP LEFT corner of the puzzle grid
3. press F2 on the BOTTOM RIGHT corner of the puzzle grid
4. press F3 to solve it

thats it.

other keys:
  F4 - tests the mouse drag so you can check its working
  F5 - prints color debug info (only useful if something isnt being detected,
       note: F5 output only shows in console, wont do anything in the exe
       version unless you run it from cmd)

the "fully complete gen (x4)" checkbox makes it run the solve 4 times in a row
   only turn this on if the generator is at 0% and hasnt been touched yet

the delay sliders control mouse speed. if inputs arent registering, slow it down.
the program autowaits if a solve finishes too fast (antikick protection)


DISCLAIMER
----------
please do not use this for malicious purposes.
using it in public servers is risky and you will likely get banned.
this was made for fun / private use only.



-----------
this is provided as-is. no warranty whatsoever.
if you get banned, kicked, or your pc catches fire thats on you.
use at your own risk. do whatever you want with it, just dont sell it or add malware to it.