#!/bin/bash
# Load user environment
source "$HOME/.profile"

# Run scraper (with error checking)
if ! python3 "$HOME/code/chattanooga_events/scraper.py"; then
    notify-send "Scraping failed!"
    exit 1
fi

# Open result (with fallback)
if ! xdg-open "$HOME/code/chattanooga_events/data/all_events.csv"; then
    libreoffice --calc "$HOME/code/chattanooga_events/data/all_events.csv" || \
    notify-send "Failed to open CSV"
fi

# TODO: run convert_image_xlsx.py
# TODO: open xlsx
# TODO: set up email configs
    # mutt: (create ~/.muttrc)
    '''
    sudo apt install mutt
    '''
    '''
    set from = "your.email@gmail.com"
    set realname = "Your Name"
    set smtp_url = "smtps://your.email@gmail.com@smtp.gmail.com:465/"
    set smtp_pass = "your-app-password"  # Use Gmail App Password
    '''
    # (Fallback) Configure /etc/ssmtp/ssmtp.conf:  (may need more configuration? Ensure that the mail command (from mailutils) is configured to use ssmtp as its delivery method)
    '''
    sudo apt-get install mailutils
    sudo apt install ssmtp uuencode
    '''
    '''
    root=your.email@gmail.com
    mailhub=smtp.gmail.com:587
    AuthUser=your.email@gmail.com
    AuthPass=your-app-password
    UseTLS=YES
    UseSTARTTLS=YES
    '''
    # add to linux-setup script
# TODO: run email script
# TODO: may need a new conda env for this
    # add to linux-setup script
# TODO: new .desktopto run this after activating conda env