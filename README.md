# rockettype
A windows keylooger to track typing statistics like WPM

- logger - Stores each keypress into and ever growing file `outputs\key_log.txt`
- Stats  - calculates WPM

DISCLAIMER: Currently *all* keypresses are logged, including passwords etc.

## Requirements
- Python 3

## Logging

`python logger.pyw`

## Statistics

`python Stats.py`

```time
2020-08-26    70
2020-08-27    65
2020-08-28    74
2020-08-29    75
Name: WPM, dtype: int32
Show the stats in real time?
```

## TODO

- GUI > Terminal > pyQT
- auto-run on Windows start > explain how to add it to shell:autorun
- more efficient logging (one file per day? > sqlite)
- Don't record passwords
- Website
- Installer https://cyrille.rossant.net/create-a-standalone-windows-installer-for-your-python-application/
