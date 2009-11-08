#!/usr/bin/env python

import numpy


class VTKICP(object):
    '''VTK ICP'''

    def __init__(self, source, target, \
        max_iterations=200, tolerance=1e-5, \
        match_centroids=True):
        object.__init__(self)
        self.source = source
        self.target = target
        self.max_iterations = max_iterations
        self.tolerance = tolerance
        self.match_centroids = match_centroids

        self._compute()

    def _compute(self):
        from vtk import vtkIterativeClosestPointTransform

        source_polydata = self.as_polydata(self.source)
        target_polydata = self.as_polydata(self.target)

        icp_transform = vtkIterativeClosestPointTransform()
        icp_transform.SetSource(source_polydata)
        icp_transform.SetTarget(target_polydata)
        icp_transform.SetMaximumNumberOfIterations(self.max_iterations)
        if self.match_centroids:
            icp_transform.StartByMatchingCentroidsOn()
        else:
            icp_transform.StartByMatchingCentroidsOff()
        icp_transform.SetMaximumNumberOfLandmarks( \
            source_polydata.GetNumberOfPoints())
        icp_transform.SetMaximumMeanDistance(self.tolerance)
        icp_transform.Update()

        matrix = icp_transform.GetMatrix()

        self.scale_and_rotation = numpy.zeros((3,3))
        self.translation = numpy.zeros(3)

        for i in range(3):
            for j in range(3):
                self.scale_and_rotation[i, j] = matrix.GetElement(i, j)

        self.translation[0] = matrix.GetElement(0, 3)
        self.translation[1] = matrix.GetElement(1, 3)
        self.translation[2] = matrix.GetElement(2, 3)

        print 'Number of iterations:', icp_transform.GetNumberOfIterations()
        print 'Scale and Rotation:\n', self.scale_and_rotation
        print 'Translation:', self.translation

    def transform(self, points):
        pts = numpy.asarray(points, dtype=float)
        return numpy.dot(points, numpy.transpose(self.scale_and_rotation)) \
            + self.translation

    def as_polydata(self, mesh):
        from vtk import vtkPoints
        from vtk import vtkCellArray
        from vtk import vtkPolyData

        if isinstance(mesh, vtkPolyData):
            return mesh

        points = vtkPoints()
        for p in mesh.points:
            points.InsertNextPoint(*p)

        polys = vtkCellArray()
        for f in mesh.indices:
            polys.InsertNextCell(len(f))
            for fv in f:
                polys.InsertCellPoint(fv)

        polydata = vtkPolyData()
        polydata.SetPoints(points)
        polydata.SetPolys(polys)
        return polydata

