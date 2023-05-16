"""
PowerFactory Python Library.
2. Load flow Calculation
author: IB
"""


class LoadFlow:
    """Run PowerFactory Loadflow."""

    def __init__(self, app):
        self.app = app
        self.ldf = None
        self.settings_are_set = False

    def ldf_init(self):
        """Get PowerFactory Loadflow Object."""
        return self.app.GetFromStudyCase("ComLdf")

    def set_settings(self, method, pst, plim, tap_trf, tap_shunt, qlim, v_deps_load, fls, active_power_ctrl, balancing):
        """Set Loadflow Settings."""

        # Calculation Method
        # 0 AC Load FLow, balanced, positive sequence (default)
        # 1 AC Load Flow, unbalanced, 3-phase (ABC)
        # 2 DC Load Flow
        self.ldf.iopt_net = method

        # Active Power Regulation
        # Automatic tap adjustment of phase shifters (default=0)
        self.ldf.iPST_at = pst
        # Consider active power limits (default=0)
        self.ldf.iopt_plim = plim

        # Voltage and Reactive Power Regulation
        if method != 3:
            # Automatic tap adjustment of transformers  (default=0)
            self.ldf.iopt_at = tap_trf
            # Automatic tap adjustment of shunts  (default=0)
            self.ldf.iopt_asht = tap_shunt
            # Consider reactive power limits  (default=0)
            self.ldf.iopt_lim = qlim

            # Load Options
            # Consider Voltage Dependency of Loads  (default=0)
            self.ldf.iopt_pq = v_deps_load
        # Feeder Load Scaling
        self.ldf.iopt_fls = fls

        # Active Power Control
        # 0 as Dispatched  (default)
        # 1 according to Secondary Control
        # 2 according to Primary Control
        # 3 according to Inertia
        self.ldf.iopt_apdist = active_power_ctrl

        # Balancing
        if self.ldf.iopt_apdist == 0:
            # 0 by reference machine (default)
            # 1 by load at reference bus
            # 2 by static generator at reference bus
            # 3 Distributed slack by loads
            # 4 Distributed slack by synchronous generators
            # 5 Distributed slack by synchronous generators and static generators
            self.ldf.iPbalancing = balancing
        return True

    def settings(self,
                 method=0,
                 pst=0,
                 plim=0,
                 tap_trf=0,
                 tap_shunt=0,
                 qlim=0,
                 v_deps_load=0,
                 fls=0,
                 active_power_ctrl=0,
                 balancing=0):
        """Call this function to set Loadflow Settings."""
        self.ldf = self.ldf_init()
        self.settings_are_set = self.set_settings(method,
                                                  pst,
                                                  plim,
                                                  tap_trf,
                                                  tap_shunt,
                                                  qlim,
                                                  v_deps_load,
                                                  fls,
                                                  active_power_ctrl,
                                                  balancing)

    def run(self):
        """Call this function to execute Loadflow. Return 0 if Loadflow was successful."""
        if self.ldf is None:
            self.ldf = self.ldf_init()
        return self.ldf.Execute()
