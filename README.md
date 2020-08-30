# RocketType

A windows keylogger to track typing statistics like WPM

- logger - Stores each keypress into and ever growing file `outputs\key_log.txt`
- Stats  - calculates WPM

The log file can be imported into other software like Pandas, Excel, PowerBI etc. to calculate other statistics

_DISCLAIMER: Currently **all** keypresses are logged, including passwords etc._

If you are interested in using this and need a feature, please let me know.

## Setup

1. Install Python 3
2. Clone repository
3. Add to your autorun (Win+R type `shell:startup` + right-click drag `logger.pyw` into the folder and select "Create shortcut here"

## Logger

#### Dependencies
Requires `pynput` and `win10toast`. Install with the following command:
`pip install pynput win10toast`

#### Starting
`python logger.pyw`

Each keypress will be stored like this:

```
time delta key application
1598479190.443632 811 'h' Notepad.exe
```

`delta` are the milliseconds since the last keypress

## Statistics

### Show
`python stats.py`

```time
2020-08-26    70
2020-08-27    65
2020-08-28    74
2020-08-29    75
Name: WPM, dtype: int32
```

### WPM (Words-per-minute) calculation :
- ignoring deltas >2 seconds (probably a deliberate pause)
- `60 seconds / (delta / 1000) / 5` (average english word length)

## TODO

### Completed:
- Enable/disable on hotkey Ctrl+Alt+R > Feedback? Console / Sound / System Notification (super easy) (1h, ~Monday night)

### On-going
- Build an [Installer](https://cyrille.rossant.net/create-a-standalone-windows-installer-for-your-python-application/)

### Small (near future)
- GUI? (Idea: pyQT) (Enable/Disable, Calculate Stats)
- Encrypt the .txt with a password? Windows User Account
- Avoid logging passwords - Idea: Have a regular expression filter that stops recording for n-chars if the beginning of the password is matched?)
- Cache process-id and process-name to avoid extraction on each keypress
- Santize:- don't store all the text,  opportuniyt bs,bs ty
- More efficient logging & stats (Ideas: one file per day?  sqlite)
- Add to auto-run on Windows start- Website

### Epic: Correct Fingers?
- record a webcam shot on each keypress and analyze whether the correct finger was used to press the key
- prevent the wrong key to register

### Epic: AutoCorrections
- Show most common typos? (Idea: Learn typos on backspace presses)
- Auto-correct typos
- Enable corrections on words that a further away (not only the last word)
- Enable "approximate" typing where you can really mess up the word you are typing

## Inspirations

### Tools

- [Universal AutoCorrect](http://www.biancolo.com/blog/autocorrect/) for [AutoHoteKey](https://www.autohotkey.com/)
- [Windows Typing Predictions](https://www.howtogeek.com/429702/how-to-enable-text-prediction-for-a-hardware-keyboard-on-windows-10/)
- [Lightkey](https://www.lightkey.io)

### Websites

- [keybr.com](https://www.keybr.com/) typing practice
- [zty.pe](https://zty.pe/) super cool typing game
- [typelit.io](https://www.typelit.io/) Improve your typing by practicing on classic literature
