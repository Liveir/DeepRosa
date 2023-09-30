"""
Deep Rosa App Runner

Main running script for DeepRosa experimenting application.

Authors: Johnfil Initan, Vince Abella, Jake Perez

"""

from Views.MainView import DeepRosaGUI

def App():
    app = DeepRosaGUI()
    app.mainloop()

if __name__ == "__main__":
    App()