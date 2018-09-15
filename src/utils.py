import math
import numpy as np
import cv2

def sign(x):
    return (1 - (x <= 0))*2 - 1


def order(p1, p2):

    if p1[0] == p2[0]:  # Vertical
        if p1[1] < p2[1]:
            return p1, p2
        else:
            return p2, p1
    else:
        if p1[0] < p2[0]:
            return p1, p2
        else:
            return p2, p1


def angle(line):
    p1 = line[0]
    p2 = line[1]
    if p1[1] == p2[1]:
        return math.pi/2
    elif p1[0] == p2[0]:
        return 0
    else:
        return math.atan2(p1[1] - p2[1], p1[0] - p2[0])


def get_face(pt1, pt2):
    if pt1[0] < pt2[0]:
        return 0  # left
    elif pt1[0] == pt2[0]:
        if pt1[1] < pt2[1]:
            return 3  # top
        else:
            return 4  # bottom
    else:
        return 2  # right

def scale(point):
    return (int(point[0] * 1000), int(point[1] * 1000))


def robot_line(width, vertex):
    print(width, vertex)
    print((vertex[0][0] - (width / 2) * math.cos(vertex[1][1]), vertex[0][1] - (width / 2) * math.sin(vertex[1][1])),
           (vertex[0][0] + (width / 2) * math.cos(vertex[1][1]), vertex[0][1] + (width / 2) * math.sin(vertex[1][1])))

    return (vertex[0][0] - (width / 2) * math.cos(vertex[1][1]), vertex[0][1] - (width / 2) * math.sin(vertex[1][1])), \
           (vertex[0][0] + (width / 2) * math.cos(vertex[1][1]), vertex[0][1] + (width / 2) * math.sin(vertex[1][1]))


def closest_point(p1, p2, p3):

    # Get closest point from p1, p2, to pe3
    # print(p1, p2, p3)
    # print(math.hypot(p1[0] - p3[0], p1[1] - p3[1]))
    # print(math.hypot(p2[0] - p3[0], p2[1] - p3[1]))
    # cv2.waitKey(0)
    if math.hypot(p1[0] - p3[0], p1[1] - p3[1]) > math.hypot(p2[0] - p3[0], p2[1] - p3[1]):
        return p2
    else:
        return p1


def get_intersect(a1, a2, b1, b2):
    """
    Returns the point of intersection of the lines passing through a2,a1 and b2,b1.
    a1: [x, y] a point on the first line
    a2: [x, y] another point on the first line
    b1: [x, y] a point on the second line
    b2: [x, y] another point on the second line
    """
    s = np.vstack([a1,a2,b1,b2])        # s for stacked
    h = np.hstack((s, np.ones((4, 1)))) # h for homogeneous
    l1 = np.cross(h[0], h[1])           # get first line
    l2 = np.cross(h[2], h[3])           # get second line
    x, y, z = np.cross(l1, l2)          # point of intersection
    if z == 0:                          # lines are parallel
        return None
    return (x/z, y/z)


def vector_to_object(objects, point):

    vect = []

    for box in objects:

        corners = [box.get_tl(), box.get_tr(), box.get_br(), box.get_bl()]
        edges = np.asarray([(corners[0], corners[1]),
                            (corners[1], corners[2]),
                            (corners[2], corners[3]),
                            (corners[3], corners[0])])

        # Angle and distance to corners
        for corner in corners:
            x = corner[0] - point[0]
            y = corner[1] - point[1]
            vect.append([math.hypot(x, y), math.atan2(y, x)])
            #print('ok')

        for edge in edges:

            # Does the edge align with x-axis? (i.e. y is within upper and lower corners of box)
            if edge[0][1] < point[1] < edge[1][1]:  # rhs
                vect.append([abs(edge[0][0] - point[0]), 0])
            elif edge[1][1] < point[1] < edge[0][1]:    # lhs
                vect.append([abs(edge[0][0] - point[0]), math.pi])

            # Does the edge align with y-axis? (i.e. x is within upper and lower corners of box)
            elif edge[0][0] < point[0] < edge[1][0]:    # top
                vect.append([abs(edge[0][1] - point[1]), math.pi / 2])
            elif edge[1][0] < point[0] < edge[0][0]:    # bottom
                vect.append([abs(edge[0][1] - point[1]), 3 * math.pi / 2])

            # Corner will be closer than edge in this case
            else:
                pass

    distances = [v[0] for v in vect]
    return vect[distances.index(min(distances))]

    # # Get index of closest edge or corner
    # minVect = vect.index(min(lineDist))
    # minCorner = cornerDist.index(min(cornerDist))
    #
    # if cornerDist[minCorner] <= lineDist[minLine]:
    #     direction = math.atan2(corners[minCorner][1] - point[1], corners[minCorner][0] - point[0])
    #     return cornerDist[minCorner], direction
    # else:
    #     return lineDist[minLine], angle(edges[minLine])