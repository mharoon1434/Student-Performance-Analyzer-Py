#imports
import pandas as pd
import numpy as np
import seaborn as sns

# Basic info for each student
class Student:
    def __init__(self, id, name, mid, terminal, assigniment):
        # data definition here
        self.id=id
        self.name=name
        self.mid=mid
        self.terminal=terminal
        self.assigniment=assigniment
    def cal_final(self):
        # calculate final result
    def compute_grade(self):
        # calculate the grade
    def convert_dict(self):
        # convert data into dict
