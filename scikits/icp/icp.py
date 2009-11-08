#!/usr/bin/env python

import numpy

from scikits.icp.transform import AffineTransform


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



class TriangleMeshICP(object):
    '''Iterative closest point (ICP) algorithm for triangle meshes.

    Properties:
    ----------
        source              source mesh
        target              target mesh
        rigid               rigid/non-rigid ICP (uniform scale)
        match_centroids     match the centtriods before run ICP
        max_iterationss     maximum iterations
        tolerance           termination condition

        current_iteration   current iteration
        scales              a list of uniform scale transforms
        rotation            a list of rotation matrices
        translations        a list of translations
        rms_errors          a list of RMS error
    '''

    def __init__(self, source, target,
                 rigid=True, match_centroids=True,
                 max_iterations=200, tolerance=1e-5):
        '''Initialize and run ICP over the source and target triangle meshes.

        Parameters:
        ----------
            source              source mesh
            target              target mesh
            rigid               rigid/non-rigid ICP (uniform scale)
            match_centroids     match the centtriods before run ICP
            max_iterationss     maximum iterations
            tolerance           termination condition

        Description:
        -----------
        This implementation of ICP is used to register the source mesh
        (only triangle mesh currently) onto the target mesh.

        The source and target meshes should be the type of Mesh.

        The rigid option specifies whether the uniform scale transform is
        allowed.

        The match_centroids option indicates whether the source mesh is moved
        such that the centroids of the source and target are matched before
        runing ICP.

        The termination condition is determined by the last two options.
        '''

        object.__init__(self)

        # meshes
        self.source = source
        self.target = target
        # options
        self.rigid = rigid
        self.match_centroids = match_centroids
        self.max_iterations = max_iterations
        self.tolerance = tolerance

        # results for every step
        self.current_iteration = 0
        self.scales = []
        self.rotations = []
        self.translations = []
        self.rms_errors = []

        self._initalize_icp()
        self._run_icp()

    def _initalize_icp(self):
        '''Initialize ICP algorithm.

        Set initial states
        '''

        # convert the points to numpy array type
        self._source_points = numpy.asarray(self.source.points)
        self._target_points = numpy.asarray(self.source.points)
        self._num_source_points = len(self._source_points)
        self._num_target_points = len(self._target_points)

        # computer centriods
        self._source_centroid = numpy.sum(self._source_points, 0)
        self._source_centroid /= self._num_source_points

        self._target_centroid = numpy.sum(self._target_points, 0)
        self._target_centroid /= self._num_target_points

    def _run_icp(self):
        '''Run ICP algorithm'''
        source_points = numpy.asarray(self.source.points)
        target_points = numpy.asarray(self.target.points)

        self.source_centroid = numpy.sum(source_points, 0) / len(source_points)
        self.target_centroid = numpy.sum(target_points, 0) / len(target_points)

        # make a local copy
        source_new = source_points.copy()

        # initial state
        self.scale = 1.0
        self.translation = numpy.zeros(3)
        self.rotation = numpy.diag(numpy.ones(3))

        self.step = 0
        self.rms_errors = []

        if self.match_centroids:
            self.translation = self.target_centroid - self.source_centroid

        for i, p in enumerate(source_points):
            source_new[i] = self.transform(p)

        print 'step %d:' % self.step

        # find closest points
        dists, indices, positions = self.target.query(source_new)
        closest_points = positions

        # compute RMS error
        disp = closest_points - source_new
        rms_error = 0
        for d in disp:
            rms_error += numpy.sqrt(numpy.dot(d, d))
        rms_error /= len(source_new)
        print 'RMS error:', rms_error

        self.rms_errors.append(rms_error)

        delta_rms_error = rms_error

        while self.step < self.max_iterations and \
            numpy.abs(delta_rms_error) > self.tolerance:

            self.step += 1
            print 'step %d:' % self.step

            # find closest points
            dists, indices, positions = self.target.query(source_new)
            closest_points = positions

            # compute registration
            affine_transform = AffineTransform(source_points, \
                closest_points, self.rigid)
            self.scale = affine_transform.scale
            self.rotation = affine_transform.rotation
            self.translation = affine_transform.translation

            # apply registration
            for i, p in enumerate(source_points):
                source_new[i] = self.transform(p)

            # compute RMS error
            disp = closest_points - source_new
            rms_error = 0
            for d in disp:
                rms_error += numpy.sqrt(numpy.dot(d, d))
            rms_error /= len(source_new)
            print 'RMS error:', rms_error

            self.rms_errors.append(rms_error)

            delta_rms_error = self.rms_errors[self.step - 1] - \
                self.rms_errors[self.step]
            print 'RMS error change:', delta_rms_error
#            assert(delta_rms_error >= 0)

        print 'registration scale:', self.scale
        print 'registration rotation:\n', self.rotation
        print 'registration translation:', self.translation


    def transform(self, points):
        return self.scale * numpy.dot(points, numpy.transpose(self.rotation)) \
            + self.translation



class PointSetICP(object):
    def __init__(self, source, target, \
        max_iterations=200, tolerance=1e-5, rigid=True, \
        match_centroids=True):
        object.__init__(self)
        self.source = source
        self.target = target
        self.max_iterations = max_iterations
        self.tolerance = tolerance
        self.rigid = rigid
        self.match_centroids = match_centroids

        self._compute()

    def _compute(self):
        # TODO
        pass
