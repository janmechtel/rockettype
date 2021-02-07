# RocketType

A local keylogger to track typing statistics like WPM on Windows.

![RocketType Screenshot](https://github.com/janmechtel/rockettype/blob/master/website/key_log_sample.png?raw=true)

The log file can be imported into other software like Pandas, Excel, PowerBI etc. to calculate statistics over time etc.

If you are looking for a particular feature, please create an [issue](https://github.com/janmechtel/rockettype/issues).

## Installation

1. Download & Install [RocketType_vx.x.exe](https://github.com/janmechtel/rockettype/releases)
2. RocketType will run after installation
3. To run again: type `RocketType` in Windows Start menu
4. Optional: add to your autorun (Win+R type shell:startup + drag the `RocketType` shorctu into the folder

## Logger

Each keypress will be stored like this:
```
time delta key application
1598479190.443632 811 'hidden' Notepad.exe
```
- `time` is epoch seconds
- `delta` are the milliseconds since the last keypress
- `key` is `'hidden'` for each key press, unless there is a `output/DEBUG/`folder.
- `application` is the name of the forgrounds window procress

### Hotkeys with notifications
* `Ctrl+Alt+R` - Toggles recording. Use it to temporarily disable the recording for passwords and such,
* `Ctrl+Alt+T` - Shows statistics
* `Ctrl+Alt+X` - Exits

## Statistics

### Show

Press `Ctrl+Alt+T` it will return  

```time
2020-08-26    70
2020-08-27    65
2020-08-28    74
2020-08-29    75
Name: WPM, dtype: int32
```

### WPM (Words-per-minute) calculation
- ignoring deltas >2 seconds (probably a deliberate pause)
- `60 seconds / (delta / 1000) / 5` (average english word length)

## TODOs

The current scope is **convenient and safe logging** for statistics and personal data collection. See [open issues](https://github.com/janmechtel/rockettype/issues)

### Epic I: correct finger?

For faster touch typing the correct finger should be used. However, to _unlearn_ using the wrong finger is quite a challenge, especially when the habit is in muscle memory already. The idea is to:

- Record a webcam shot on each keypress
- Analyze whether the correct finger was used to press the key either through openCV or deep learning
- Prevent the wrong key to register

### Epic II: Auto-Correct

Typos are a big slow down for many typists. Auto-Correct is a way to combat that.

- Show most common typos? (Idea: Learn typos on backspace presses)
- Auto-correct typos - probably this can be more aggressive compared to other tools.
- Suggest corrections on words that a further away not only the last word like other tools
- _Approximate typing_ let's you really mess up the word you are typing, similar to swipe typing on mobile, which doesn't need much accurary to figure out the word you mean

####  Auto-Correct Tools for inspiration

- [Universal AutoCorrect](http://www.biancolo.com/blog/autocorrect/) for [AutoHoteKey](https://www.autohotkey.com/)
- [Windows Typing Predictions](https://www.howtogeek.com/429702/how-to-enable-text-prediction-for-a-hardware-keyboard-on-windows-10/)
- [Lightkey](https://www.lightkey.io)

## Websites

- [keybr.com](https://www.keybr.com/) typing practice
- [zty.pe](https://zty.pe/) super cool typing game
- [typelit.io](https://www.typelit.io/) Improve your typing by practicing on classic literature

## Run locally

1. Install Python 3
2. Clone Repository
3. Install requirements: `pip install pynput win10toast PyQt5`
4. Run `python startkeylogger.pyw`
5. Optional: add to your autorun (Win+R type `shell:startup` + right-click drag `logger.pyw` into the folder and select "Create shortcut here"

Debug mode: Create a DEBUG folder `mkdir output\DEBUG` (optional)

_DISCLAIMER: In Debug mode **all** keypresses are logged, including passwords etc. See: [Avoid storing passwords](https://github.com/janmechtel/rockettype/issues/6)_

## How to release

1. Install NSIS (?)
2. Make sure you hack pyapp.nsi as descriped in the my_pyapp.nsi
3. Modify your local pynsist/wheels.py as described [here](https://github.com/janmechtel/rockettype/issues/18#issuecomment-686708771)
3. `python -m nsist installer.cfg`
4. [Create a new release](https://github.com/janmechtel/rockettype/releases/new) and upload the .exe
