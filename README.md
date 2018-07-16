# Detect broken recordings

## Installation

Assuming python3 and virtualenv are present:

```python
virtualenv -p python3 env
source env/bin/activate
pip install -r requirements.txt
sudo apt install python3-tk

python main.py [.wav files here]
```

## What my solution actually does

Essentially, what I found out that works is comparing samples with drops in amplitude
to samples which come from some silent part of the same recording.  
My reasoning behind this is that true silence should have the same distribution everywhere.
I'm also assuming that there exists a particularly long moment of silence in the recording, somewhere at the beggining or end.  
For comparison I'm using Kolmogorov-Smirnov test.  
Python code is somewhat commented and readable (just start from line 230),
however, I don't recommend trying to read my R code; it may or may not contain occasional profanities.  
