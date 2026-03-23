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

no. i get why it looks sketchy though. heres why it isnt:

- `forsaken_autogen.py` has the full source code, you can read every single line before running anything
- if you know python you can just run that directly and skip the exe entirely
- the exe is literally just the python script compiled into a standalone file so people dont have to install python themselves
- you can verify the exe yourself at [virustotal.com](https://www.virustotal.com) - pyinstaller exes sometimes get 1-2 false positives from paranoid scanners, thats a known pyinstaller thing not malware

if you still dont trust it, use the PY version. thats literally why its there.

---

## which version do i use?

| option | what it is |
|---|---|
| `forsaken_autogen.exe` | download from the [releases page](../../releases/latest) and run. easiest option, nothing to install except the driver. recommended for most people |
| `forsaken_autogen.py` | raw python source. for tech savvy people, or if the exe gives you issues. requires python + a few pip installs |

---

## setup - exe version

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

## setup - PY version

**1.** install python if you havent: https://python.org

**2.** open cmd and run:
```
pip install keyboard pyautogui pillow pywin32 interception-python
```

**3.** install the interception driver (same steps as above, still required)

**4.** after reboot run:
```
python forsaken_autogen.py
```

---

## how to use

1. open the game and stand in front of a generator puzzle
2. press `F1` to open the grid draw overlay
3. click and drag over **the dark greyish cells only** - not the white border around them and not the pure black gaps. the playfield itself is a slightly greyish dark, sooo draw on that ye
4. press `F3` to solve it

thats it

### hotkeys

| key | what it does |
|---|---|
| `F1` | opens the grid draw overlay |
| `F3` | starts the solver |
| `F4` | tests the mouse drag so you can check its working |
| `F5` | prints color detection debug info to console |
| `F6` | runs path trace analysis - visualizes the solve without touching your mouse |

> any key that isnt F1-F6 will abort the solver and close the visualizer mid-run

### settings

**repeat 4x** - runs the solve 4 times in a row. only turn this on if the generator is at 0% and hasnt been touched at all yet (and if ur lazy to press f3 every new puzzle)

**speed multiplier** - controls how fast the mouse moves between cells. if inputs arent registering slow it down. if you want it faster crank it up

### path trace analysis (F6)

press `F6` instead of `F3` to run a visualization-only mode. it solves the grid, draws the DFS exploration in real time, animates all the paths, then simulates the drag sequence visually with sfx, without ever touching your mouse or clicking anything ingame. useful for checking if the detection is correct before committing to a real solve. closes itself automatically after finishing.

### missed pair retry

after the solver finishes dragging all paths it takes a fresh screenshot and checks if any pairs didnt register. if it finds any it automatically reattempts those specific paths without redoing the whole grid.

---

## disclaimer

please do not use this for malicious purposes. using it in public servers is risky and you will likely get banned. this was made for fun / private use only. be smart about it.

provided as-is, no warranty whatsoever. if you get banned, kicked, or your pc catches fire thats on you. use at your own risk. do whatever you want with it, just dont sell it or add malware to it lol
