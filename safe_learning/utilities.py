"""
Utilities for plotting, function definitions, and GPs.

This file defines utilities needed for the experiments, such as creating
parameter grids, computing LQR controllers, Lyapunov functions, sample
functions of Gaussian processes, and plotting ellipses.

Author: Felix Berkenkamp, Learning & Adaptive Systems Group, ETH Zurich
        (GitHub: befelix)
"""

from __future__ import division, print_function

from collections import Sequence

import numpy as np
import scipy.interpolate
import scipy.linalg

__all__ = ['combinations', 'linearly_spaced_combinations', 'lqr',
           'ellipse_bounds']


def combinations(arrays):
    """Return a single array with combinations of parameters.

    Parameters
    ----------
    arrays : list of np.array

    Returns
    -------
    array : np.array
        An array that contains all combinations of the input arrays
    """
    return np.array(np.meshgrid(*arrays)).T.reshape(-1, len(arrays))


def linearly_spaced_combinations(bounds, num_samples):
    """
    Return 2-D array with all linearly spaced combinations with the bounds.

    Parameters
    ----------
    bounds : sequence of tuples
        The bounds for the variables, [(x1_min, x1_max), (x2_min, x2_max), ...]
    num_samples : integer or array_likem
        Number of samples to use for every dimension. Can be a constant if
        the same number should be used for all, or an array to fine-tune
        precision. Total number of data points is num_samples ** len(bounds).

    Returns
    -------
    combinations : 2-d array
        A 2-d arrray. If d = len(bounds) and l = prod(num_samples) then it
        is of size l x d, that is, every row contains one combination of
        inputs.
    """
    num_vars = len(bounds)
    if not isinstance(num_samples, Sequence):
        num_samples = [num_samples] * num_vars

    # Create linearly spaced test inputs
    inputs = [np.linspace(b[0], b[1], n) for b, n in zip(bounds,
                                                         num_samples)]

    # Convert to 2-D array
    return combinations(inputs)


def lqr(A, B, Q, R):
    """
    Compute the continuous time LQR-controller.

    Parameters
    ----------
    A : np.array
    B : np.array
    Q : np.array
    R : np.array

    Returns
    -------
    K : np.array
        Controller matrix
    P : np.array
        Cost to go matrix
    """
    P = scipy.linalg.solve_continuous_are(A, B, Q, R)

    # LQR gain
    K = np.linalg.solve(R, B.T.dot(P))

    return K, P


def ellipse_bounds(P, level, n=100):
    """Compute the bounds of a 2D ellipse.

    The levelset of the ellipsoid is given by
    level = x' P x. Given the coordinates of the first
    dimension, this function computes the corresponding
    lower and upper values of the second dimension and
    removes any values of x0 that are outside of the ellipse.

    Parameters
    ----------
    P : np.array
        The matrix of the ellipsoid
    level : float
        The value of the levelset
    n : int
        Number of data points

    Returns
    -------
    x : np.array
        1D array of x positions of the ellipse
    yu : np.array
        The upper bound of the ellipse
    yl : np.array
        The lower bound of the ellipse

    Notes
    -----
    This can be used as
    ```plt.fill_between(*ellipse_bounds(P, level))```
    """
    # Round up to multiple of 2
    n += n % 2

    # Principal axes of ellipsoid
    eigval, eigvec = np.linalg.eig(P)
    eigvec *= np.sqrt(level / eigval)

    # set zero angle at maximum x
    angle = np.linspace(0, 2 * np.pi, n)[:, None]
    angle += np.arctan(eigvec[0, 1] / eigvec[0, 0])

    # Compute positions
    pos = np.cos(angle) * eigvec[:, 0] + np.sin(angle) * eigvec[:, 1]
    n /= 2

    # Return x-position (symmetric) and upper/lower bounds
    return pos[:n, 0], pos[:n, 1], pos[:n - 1:-1, 1]
