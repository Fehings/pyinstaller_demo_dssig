# pyinstaller_examples_dssig

## Instructions for use

Clone this repository:
`git clone git@github.com:Fehings/pyinstaller_demo_dssig.git`

Setup:

`python -m venv ./.env`
`pip install -r requirements.txt`

There are two apps to try with pyinstaller, a pyside6 based one, and a shiny one. 

The pyside6 one is run as any script:
`python transplant_policy_gui.py`

To run the shiny app, you need to do:
`shiny run app.py`

Then navigate to 127.0.0.1:8000 on your web browser to view the application.

## Tasks:

1. Get pyinstaller to work for the transplant_policy_gui

2. Get pyinstaller to work for the shiny app

3. Modify the apps to pull the policy options from the yaml file 

4. Retry the installation, can you include the yaml file in the executable?

