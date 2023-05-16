"""
Created on Tue Apr 19 18:02:08 2022.

@author: IB
"""

import sys
import numpy as np

class PowerFactory:
    """PowerFactory Main Class."""

    def __init__(self, path):
        self.path = path
        self.app = None
        self.user = None
        self.project = None

    @staticmethod
    def clear_path():
        """Delete previous PowerFactory Versions in path."""
        index = []
        for i, path in enumerate(sys.path):
            if "PowerFactory" not in path:
                index.append(i)
        new_path = [sys.path[i] for i in index]
        sys.path = new_path
        return True

    def add_path(self):
        """Add directory of powerfactory module to sys.path."""
        return sys.path.append(self.path)

    def get_user(self):
        """Get current user."""
        return self.app.GetCurrentUser()

    def activate_project(self, project_name):
        """Open Project.

        TODO: Fehlerhandling, wenn Projekt nicht gefunden wird.
        """
        if self.user is None:
            self.user = self.get_user()
        project = self.user.GetContents(project_name + ".IntPrj")[0]
        return project.Activate()

    def open_app(self, project_name):
        """Open PowerFactory Application and activate project.

        Return PowerFactory application.

        TODO: Problem bei Import powerfactory Modul, wenn mehrere
        PowerFactory Versionen in sys.path! Import sollte @toplevel sein.
        TODO: Fehlerhandling wenn PowerFactory nicht importiert werden kann.
        """
        self.clear_path()
        self.add_path()

        import powerfactory as pf

        if self.app is None:
            self.app = pf.GetApplicationExt()
        if self.project is None:
            self.project = self.activate_project(project_name)

        return self.app
