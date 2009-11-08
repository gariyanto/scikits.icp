#!/usr/bin/env python

import numpy

from scikits.icp.quaternion import Quaternion


class AffineTransform(object):
    '''Compute the affine transform between the source and target point
    sets.
    
    Properties:
        translation
        scale
        rotation
    '''

    def __init__(self, source, target, calc_scale=True):
        object.__init__(self)
        self.source = numpy.asarray(source)
        self.target = numpy.asarray(target)
        self._calc_scale = calc_scale

        self.translation = numpy.zeros(3)
        self.scale = 1.0
        self.quaternion = Quaternion()
        self.matrix_R = self.quaternion.as_matrix3x3()

        assert(self.source.shape == self.target.shape)
        assert(self.source.shape[1] == 3)
        assert(self.source.shape[0] > 0)

        self._num_points = self.source.shape[0]

        self._compute_affine_transformation()

        self.rotation = self.matrix_R

    def _compute_affine_transformation(self):
        """Compute the optimal orientation (scale, rotation, translation)
        between two point sets"""

        # compute the centriods
        self.source_centriod = numpy.sum(self.source, 0) / self._num_points
        self.target_centriod = numpy.sum(self.target, 0) / self._num_points

        # substract each coordinate by centriod
        self.source -= self.source_centriod
        self.target -= self.target_centriod

        #-----------------------------
        # compute the optimal rotation
        #-----------------------------

        # compute the cross-covariance matrix
        cov_matrix = numpy.zeros((3,3))
        for source_p, target_p in zip(self.source, self.target):
            cov_matrix += source_p[:, numpy.newaxis] * target_p
        cov_matrix /= self._num_points

        matrix_N = self._compute_matrix_N(cov_matrix)

        # compute the eigenvalues of the 4x4 matrix N
        eigenvalues, eigen_vectors = numpy.linalg.eig(matrix_N)

        # sort eigenvalues: largest -> smallest
        sorted_indices = numpy.argsort(eigenvalues)[::-1]
        assert(eigenvalues[sorted_indices[0]] > 0)

        # the corresponding eigen vector is selected as the optimal quaternion
        # refer Horn1987
        quaternion = eigen_vectors[:, sorted_indices[0]]
        print 'the optimal quaternion:', quaternion
        self.quaternion = Quaternion(*quaternion)


        #--------------------------
        # compute the optimal scale
        #--------------------------

        if self._calc_scale:
            source_d = 0
            for source_p in self.source:
                source_d += numpy.dot(source_p, source_p)
            target_d = 0
            for target_p in self.target:
                target_d += numpy.dot(target_p, target_p)

            self.scale = numpy.sqrt(target_d / source_d)
            print "the optimal scale:", self.scale

        #--------------------------------
        # compute the optimal translation
        #--------------------------------

        self.matrix_R = self.quaternion.as_matrix3x3()
        self.translation = self.target_centriod - \
            self.scale * numpy.dot(self.matrix_R, self.source_centriod)
        print 'the optimal translation:', self.translation

    def _compute_matrix_N(self, cov_matrix):
        """Compute the matrix N (refer to Horn1987, Besl1992)"""
        assert(cov_matrix.shape == (3,3))

        trace = numpy.trace(cov_matrix)
        cov_matrix_t = numpy.transpose(cov_matrix)
        matrix_I = numpy.diag(numpy.ones(3))

        # anti-symmetric matrix A (Besl1992)
        matrix_A = cov_matrix - cov_matrix_t
        delta = numpy.array([matrix_A[1,2], matrix_A[2,0], matrix_A[0,1]])

        # submatrix of the matrix N
        sub_matrix = cov_matrix + cov_matrix_t - trace * matrix_I

        # refer to Besl1992
        matrix_N = numpy.zeros((4,4))
        matrix_N[0, 0] = trace
        matrix_N[0, 1:] = delta
        matrix_N[1:, 0] = delta
        matrix_N[1:, 1:] = sub_matrix

        return matrix_N


    def transform(self, point):
        return self.scale * numpy.dot(self.matrix_R, numpy.asarray(point)) + \
            self.translation
