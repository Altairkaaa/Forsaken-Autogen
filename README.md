```
___________                          __                       _____          __              ________               
\_   _____/__________  ___________  |  | __ ____   ____      /  _  \  __ ___/  |_  ____     /  _____/  ____   ____  
 |    __)/  _ \_  __ \/  ___/\__  \ |  |/ // __ \ /    \    /  /_\  \|  |  \   __\/  _ \   /   \  ____/ __ \ /    \ 
 |     \(  <_> )  | \/\___ \  / __ \|    <\  ___/|   |  \  /    |    \  |  /|  | (  <_> )  \    \_\  \  ___/|   |  \
 \___  / \____/|__|  /____  >(____  /__|_ \\___  >___|  /  \____|__  /____/ |__|  \____/    \______  /\___  >___|  /
     \/                   \/      \/     \/    \/     \/           \/                              \/     \/     \/ 
```
---
## wait, is this a virus?
no. i get why it looks sketchy though
heres why it isnt:
- `forsaken_solver.py` has the full source code, you can read every single line before running anything
- if you know python you can just run that directly and skip the exe entirely
- the exe is literally just the python script compiled into a standalone file so people dont have to install python themselves
- you can verify the exe yourself at [virustotal.com](https://www.virustotal.com), pyinstaller exes sometimes get 1-2 false positives from paranoid scanners, thats a known pyinstaller thing not malware
if you still dont trust it, use the PY version. thats literally why its there.
---
## which version do i use?
| option | what it is |
|---|---|
| `forsaken_autogen.exe` | download from the [releases page](../../releases/latest) and run. easiest option, nothing to install except the driver. recommended for most people |
| `forsaken_solver.py` | raw python source. for tech savvy people, or if the exe gives you issues. requires python + a few pip installs |
---
## setup — exe version
**1.** download `forsaken_autogen.exe` from the [releases page](../../releases/latest)

you also need to install ONE thing and its a driver called interception.

**2.** download it here: https://github.com/oblitum/Interception/releases
**3.** inside the zip theres a file called `install-interception.exe`, right click it and run as administrator
**4.** in the cmd window that opens type:
```
install-interception.exe /install
```
**5.** save all your work then restart your pc (it needs a restart coz its a driver)
**6.** after reboot run `forsaken_autogen.exe` and ya good
---
## setup — PY version
**1.** install python if you havent: https://python.org
**2.** open cmd and run:
```
pip install keyboard pyautogui pillow pywin32 interception-python
```
**3.** install the interception driver (same steps as above, still required)
**4.** after reboot run:
```
python forsaken_solver.py
```
---
## how to use
1. open the game and stand in front of a generator puzzle
2. press `F1` on the **top left** corner of the puzzle grid
3. press `F2` on the **bottom right** corner of the puzzle grid
4. press `F3` to solve it
thats it. seriously.
**other keys:**
| key | what it does |
|---|---|
| `F4` | tests the mouse drag so you can check its working |
| `F5` | prints color debug info, only useful if something isnt being detected. note: only shows in console, wont do anything in the exe version unless you run it from cmd |
**"fully complete gen (x4)" checkbox** makes it run the solve 4 times in a row. only turn this on if the generator is at 0% and hasnt been touched yet

**delay sliders** control mouse speed. if inputs arent registering, slow it down. the program autowaits if a solve finishes too fast (antikick protection)

---
## disclaimer
please do not use this for malicious purposes. using it in public servers is risky and you will likely get banned. this was made for fun / private use only. be smart about it.
provided as-is, no warranty whatsoever. if you get banned, kicked, or your pc catches fire thats on you. use at your own risk. do whatever you want with it, just dont sell it or add malware to it lol
```
