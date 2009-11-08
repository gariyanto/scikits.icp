#!/usr/bin/env python

import os
import numpy

from scikits.mesh import Mesh


def generate_wave(noise=0.05):
    x = numpy.r_[-2*numpy.pi:2*numpy.pi:0.5]
    y = numpy.r_[-2*numpy.pi:2*numpy.pi:0.5]
    z = numpy.cos(x).reshape(len(x), 1) + numpy.sin(y) + \
        numpy.random.randn(len(x), len(y)) * noise

    points = []
    for i in range(len(x)):
        for j in range(len(y)):
            points.append([x[i], y[j], z[i, j]])

    indices = []
    for i in range(len(x) - 1):
        for j in range(len(y) - 1):
            i0 = i*len(x) + j
            i1 = (i+1)*len(x) + j
            i2 = (i+1)*len(x) + j+1
            i3 = i*len(x) + j+1
            indices.append([i0, i2, i3])
            indices.append([i0, i1, i2])

    return Mesh(points, indices)


if __name__ == '__main__':
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    wave_file1 = os.path.join(output_dir, 'wave1.off')
    wave_file2 = os.path.join(output_dir, 'wave2.off')

    wave1 = generate_wave(0.1)
    wave2 = generate_wave(0.2)

    angle = numpy.pi / 6
    rotation = numpy.zeros((3,3))
    rotation[0, 0] = numpy.cos(angle)
    rotation[1, 1] = rotation[0, 0]
    rotation[0, 1] = -numpy.sin(angle)
    rotation[1, 0] = -rotation[0, 1]
    rotation[2, 2] = 1

    new_points = []
    for p in wave2.points:
        new_points.append(numpy.dot(rotation, p) + numpy.array([1, 0, 3]))

    wave2 = Mesh(new_points, wave2.indices)

    wave1.write(wave_file1)
    wave2.write(wave_file2)
