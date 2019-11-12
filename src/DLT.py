import numpy as np
from numpy import linalg as la
from naiveAlgorithm import naive_algorithm


def get_2_x_9_matrix(A, B):
    matrix = np.array([
        [0, 0, 0, -B[2]*A[0], -B[2]*A[1], -B[2]*A[2], B[1]*A[0], B[1]*A[1], B[1]*A[2]],
        [B[2]*A[0], B[2]*A[1], B[2]*A[2], 0, 0, 0, -B[0]*A[0], -B[0]*A[1], -B[0]*A[2]]
    ])
    
    return matrix


def dlt(dots, dots_after):
    C = get_2_x_9_matrix(dots[0], dots_after[0])
    n = len(dots)

    for i in range(1, n):
        N = get_2_x_9_matrix(dots[i], dots_after[i])
        C = np.concatenate((C, N))

    _, _, V_t = la.svd(C)
    V = np.transpose(V_t)

    P = V[:, -1]
    P = P.reshape(3, 3)

    return P


def show_dlt(dots, dots_after):
    P = dlt(dots, dots_after)

    # print("Pokazivanje da se dobija ista matrica kao sa naivnim algoritmom")

    if len(dots) > 4:
        dots_naive = dots[:4]
        dots_after_naive = dots_after[:4]
        P_naive = naive_algorithm(dots_naive, dots_after_naive)
    else:
        P_naive = naive_algorithm(dots, dots_after)

    for i in range(3):
        for j in range(3):
            P[i, j] = round(P[i, j], 5)

    # print("Zaokruzeno na 5 decimala:")
    # print(P)
    # print()

    for i in range(3):
        for j in range(3):
            if P_naive[i, j] != 0 and P[i, j] != 0:
                P = P / P[i, j] * P_naive[i, j]

                # print("Delimo sa P[" + str(i) + ", " + str(j) + "]")
                # print(P)

                return P
