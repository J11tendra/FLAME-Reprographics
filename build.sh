#!/bin/bash
pip install --upgrade pip
pip install -r requirements.txt
pip freeze | grep PyMuPDF  # Check the installed version
