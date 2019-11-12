from naiveAlgorithm import naive_algorithm
from DLT import dlt

import numpy as np
from numpy import linalg as la
from functools import reduce


def normalize(dots):
    dots_afine = [(dot[0]/dot[2], dot[1]/dot[2], 1) for dot in dots]

    c = tuple(reduce(lambda x, y: x+y, map(lambda x: np.array(x), dots_afine)))
    c = np.array(c) / len(dots_afine)

    G = np.array([[1, 0, -c[0]],
                  [0, 1, -c[1]],
                  [0, 0, 1]])

    dots_afine_new = [G.dot(np.array(dot)) for dot in dots_afine]
    distances = [np.sqrt(d[0]*d[0] + d[1]*d[1]) for d in dots_afine_new]

    lamda = sum(distances) / len(dots_afine_new)

    k = np.sqrt(2) / lamda

    H = np.array([[k, 0, 0],
                  [0, k, 0],
                  [0, 0, 1]])

    T = np.dot(H, G)

    # print("Matrica normalizacije: ")
    # print(T)
    # print()

    return [T.dot(np.array(dot)) for dot in dots], T


def normalized_dlt(dots, dots_after):
    dots_normalized, T = normalize(dots)
    dots_after_normalized, T_after = normalize(dots_after)

    P_normalized = dlt(dots_normalized, dots_after_normalized)
    P = np.dot(np.dot(la.inv(T_after), P_normalized), T)

    # print("Matrica dobijena normalizovanim algoritmom:")
    # print(P)
    # print()

    return P


def show_normalized(dots, dots_after):
    P = normalized_dlt(dots, dots_after)

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

    # print("Pokazivanje da je isto kao kod prethodnih algoritama:")

    for i in range(3):
        for j in range(3):
            if P_naive[i, j] != 0 and P[i, j] != 0:
                P = P / P[i, j] * P_naive[i, j]

                # print("Delimo sa P[" + str(i) + ", " + str(j) + "]")
                # print(P)

                return P
