#!/usr/bin/env python

import os

from scikits.mesh import Mesh
from scikits.icp import VTKICP
from scikits.icp.utils import data_dir


def test_vtk_icp():
    source_file = os.path.join(data_dir(), 'wave1.off')
    target_file = os.path.join(data_dir(), 'wave2.off')

    source_mesh = Mesh(source_file)
    target_mesh = Mesh(target_file)

    vtk_icp = VTKICP(source_mesh, target_mesh)

    points = vtk_icp.transform(source_mesh.points)
    new_mesh = Mesh(points, source_mesh.indices)
    new_mesh.write('/tmp/wave.off')

if __name__ == '__main__':
    test_vtk_icp()
