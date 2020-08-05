# Tor-Voting-Bot

This bot creates fake votes for the youth word of the year poll of the Langenscheidt Verlag.
Appears to not work since Surveymonkey appears to have blocked every tor exit node IP.
Still leave it up for future reference if I want to use tor exit node switching for some script.

## Setup

### Prerequisite

Use Linux (at least only tested with it) and have python3 installed

## Setup process

1. Install tor e.g. on debian `sudo apt install tor`
2. (Optional) Create virtual environment `virtualenv venv`
    * And activate via `source venv/bin/activate`
3. Install required packages `pip install -r ./requirements.txt`
4. Edit the wanted word `VOTE_WORD` in `torRequests.py`
5. Start `python ./torRequests.py`
