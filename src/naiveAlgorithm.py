import numpy as np
from numpy import linalg as la
import sys


def get_G_matrix(A, B, C, D):
    delta = np.array([
        [A[0], B[0], C[0]],
        [A[1], B[1], C[1]],
        [A[2], B[2], C[2]]
    ])
    
    delta_x = np.array([
        [D[0], B[0], C[0]],
        [D[1], B[1], C[1]],
        [D[2], B[2], C[2]]
    ])
    
    delta_y = np.array([
        [A[0], D[0], C[0]],
        [A[1], D[1], C[1]],
        [A[2], D[2], C[2]]
    ])
    
    delta_z = np.array([
        [A[0], B[0], D[0]],
        [A[1], B[1], D[1]],
        [A[2], B[2], D[2]]
    ])

    det = la.det(delta)
    det_x = la.det(delta_x)
    det_y = la.det(delta_y)
    det_z = la.det(delta_z)

    if det == 0:
        if det_x == det_y and det_y == det_z and det_z == 0:
            sys.exit("Sistem ima beskonacno mnogo resenja!")
        else:
            sys.exit("Sistem nema resenja!")

    alpha = det_x / det
    beta = det_y / det
    gamma = det_z / det

    P = np.array([
        [alpha * A[0], beta * B[0], gamma * C[0]],
        [alpha * A[1], beta * B[1], gamma * C[1]],
        [alpha * A[2], beta * B[2], gamma * C[2]]
    ])

    return P


def naive_algorithm(dots, dots_after):
    G = get_G_matrix(dots[0], dots[1], dots[2], dots[3])
    G_minus = la.inv(G)
    H = get_G_matrix(dots_after[0], dots_after[1], dots_after[2], dots_after[3])
    F = H.dot(G_minus)

    return F
