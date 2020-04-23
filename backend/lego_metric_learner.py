# Adapted from https://bitbucket.org/muckdoc/muckdoc/
# Look into faster version, e.g. from https://github.com/fcaldas/MetricLearning/blob/master/lego_functions.py

import numpy as np


def lego(u, v, y, r=0.5, A_prev=None):
    # TODO: Doc string from Sriram

    m = len(u)  # number of features
    # make into colume vectors [m,1]
    u = u[:, np.newaxis]
    v = v[:, np.newaxis]
    if A_prev is None:
        A_prev = np.identity(m)

    # find the current distance (mahalanobis) between u and v
    z = u - v
    y_current = float(np.dot(z.T, np.dot(A_prev, z)))  # y_hat in paper

    # find y_bar, which is an approximation of distance using the new metric
    y_bar_up = (
        r * y * y_current
        - 1
        + np.sqrt((r * y * y_current - 1) ** 2 + 4 * r * y_current ** 2)
    )
    y_bar_down = 2 * r * y_current
    y_bar = y_bar_up / y_bar_down
    y_bar = float(np.nan_to_num(y_bar))

    # calculate the new metric matrix A_new using y_bar
    A_new_up = r * (y_bar - y) * np.dot(A_prev, np.dot(np.dot(z, z.T), A_prev))
    A_new_down = 1 + r * (y_bar - y) * y_current
    A_new = A_prev - A_new_up / A_new_down

    return A_new


# iterates through the constraints and updates the A matrix
# TODO: look into min_max_ys. What does it do? Copied these values from pickled file
def batch_update(tfidf_mat, constraints, min_max_ys=[7, 10], A_=None):
    # TODO: Doc string from Sriram
    for doc_u, doc_v, same_class in constraints:
        u_t = tfidf_mat[doc_u]
        v_t = tfidf_mat[doc_v]
        if same_class == 1:
            y_t = min_max_ys[0]
        else:
            y_t = min_max_ys[1]
        A_ = lego(u_t, v_t, y_t, A_prev=A_)
    return A_
