"""
Deep Rosa App Runner

Main running script for DeepRosa experimenting application.

Authors: Johnfil Initan, Vince Abella, Jake Perez

"""
from Server.serverConnection import start_server
from Views.MainView import DeepRosaGUI

def dprosa():
    
    app = DeepRosaGUI()
    app.mainloop()

if __name__ == "__main__":
    # start_server()
    dprosa()