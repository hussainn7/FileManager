# -*- coding: utf-8 -*-
import sys, os

# Add project directory to the sys.path
sys.path.insert(0, '/home/u/undercover/getecu')
sys.path.insert(1, '/home/u/undercover/.local/lib/python3.6/site-packages')

from app import app as application

# Disable debug mode in production
application.debug = False 