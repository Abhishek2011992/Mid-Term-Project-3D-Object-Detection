# ---------------------------------------------------------------------
# Project "Track 3D-Objects Over Time"
# Copyright (C) 2020, Dr. Antje Muntzinger / Dr. Andreas Haja.
#
# Purpose of this file : Kalman filter class
#
# You should have received a copy of the Udacity license together with this program.
#
# https://www.udacity.com/course/self-driving-car-engineer-nanodegree--nd013
# ----------------------------------------------------------------------
#

# imports
import numpy as np

# add project directory to python path to enable relative imports
import os
import sys
PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
import misc.params as params 

class Filter:
    '''Kalman filter class'''
    def __init__(self):
        self.dt = params.dt
        self.q = params.q
        self.dim_state = params.dim_state

    def F(self):
        F = np.matrix([[1, 0, 0, self.dt, 0, 0],
                       [0, 1, 0, 0, self.dt, 0],
                       [0, 0, 1, 0, 0, self.dt],
                       [0, 0, 0, 1, 0, 0],
                       [0, 0, 0, 0, 1, 0],
                       [0, 0, 0, 0, 0, 1]])
        return F

    def Q(self):
        q = self.q
        dt = params.dt
        q3 = ((dt ** 3) / 3) * q
        q2 = ((dt ** 2) / 2) * q
        q1 = dt * q
        Q = np.matrix([[q3, 0, 0, q2, 0, 0],
                       [0, q3, 0, 0, q2, 0],
                       [0, 0, q3, 0, 0, q2],
                       [q2, 0, 0, q1, 0, 0],
                       [0, q2, 0, 0, q1, 0],
                       [0, 0, q2, 0, 0, q1]])

        return Q

    def predict(self, track):
        F = self.F()
        x = F * track.x
        P = F * track.P * F.transpose() + self.Q()
        track.set_x(x)
        track.set_P(P)
        return x, P

    def update(self, track, meas):
        H = meas.sensor.get_H(track.x)
        S = self.S(track, meas, H)
        gamma = self.gamma(track, meas)
        K = track.P * H.transpose() * np.linalg.inv(S)
        x = track.x + K * gamma
        I = np.identity(self.dim_state)
        P = (I - K * H) * track.P
        track.set_x(x)
        track.set_P(P)
        track.update_attributes(meas)

    def gamma(self, track, meas):
        return (meas.z - meas.sensor.get_hx(track.x))

    def S(self, track, meas, H):
        return H * track.P * H.transpose() + meas.R
