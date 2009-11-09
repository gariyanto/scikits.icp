#!/usr/bin/env python

import os

from scikits.mesh import Mesh
from scikits.icp import TriangleMeshICP
from scikits.icp.utils import data_dir


def test_triangle_mesh_icp():
    source_file = os.path.join(data_dir(), 'wave1.off')
    target_file = os.path.join(data_dir(), 'wave2.off')
    output_file = os.path.join(tempfile.gettempdir(), 'wave.off')

    source_mesh = Mesh(source_file)
    target_mesh = Mesh(target_file)

    triangle_mesh_icp = TriangleMeshICP(source_mesh, target_mesh, rigid=True)

    points = triangle_mesh_icp.transform(source_mesh.points)
    new_mesh = Mesh(points, source_mesh.indices)
    new_mesh.write(output_file)


if __name__ == '__main__':
    test_triangle_mesh_icp()
