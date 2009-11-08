#!/usr/bin/env python

import numpy

# http://en.wikipedia.org/wiki/Quaternion

class Quaternion(object):

    def __init__(self, a=0, b=0, c=0, d=0):
        object.__init__(self)
        self.a = a
        self.b = b
        self.c = c
        self.d = d

    def __add__(self, other):
        return Quaternion(self.a + other.a, self.b + other.b, \
            self.c + other.c, self.d + other.d)

    def __iadd__(self, other):
        self.a += other.a
        self.b += other.b
        self.c += other.c
        self.d += other.d

    def as_matrix3x3(self):
        q0 = self.a
        q1 = self.b
        q2 = self.c
        q3 = self.d

        # here, we compute a 3x3 matrix, instead of 4x4 matrix
        # refer to Besl1992
        matrix_R = numpy.zeros((3,3))
        matrix_R[0, 0] = q0*q0 + q1*q1 - q2*q2 - q3*q3
        matrix_R[1, 1] = q0*q0 + q2*q2 - q1*q1 - q3*q3
        matrix_R[2, 2] = q0*q0 + q3*q3 - q1*q1 - q2*q2

        matrix_R[0, 1] = 2*(q1*q2 - q0*q3)
        matrix_R[1, 0] = 2*(q1*q2 + q0*q3)

        matrix_R[0, 2] = 2*(q1*q3 + q0*q2)
        matrix_R[2, 0] = 2*(q1*q3 - q0*q2)

        matrix_R[1, 2] = 2*(q2*q3 - q0*q1)
        matrix_R[2, 1] = 2*(q2*q3 + q0*q1)

        return matrix_R
