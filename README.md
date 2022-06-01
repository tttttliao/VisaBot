# VisaBot
## Dependencies
To install dependencies, run:
```
pip install beautifulsoup4
pip install selenium
pip install webdriver-manager
pip install twilio
```
## Fill in information
In visa.py, fill in user-specific information in constants from line 23 to 31.

For firefox profile, go to "about:profiles" in Firefox and copy Root Directory of the profile in use.
Do not change url.
IRCC number is the number you are assigned with when you applied for Canada Visa.
To generate a Github Token, go to Settings -> Developer Settings -> Personal Access Tokens and follow the prompts.

## Modes
There are two modes for the bot. If alerts only is set to True, the program will send you an email when an appointment opens up. If set to False, the program will book the slot for you.
