import numpy as np

def min_point_x(points, indicies=None):
    '''
    calculates the point in points with minimum x value
    if `indicies` is specified, the index of the point is also returned
    '''
    min_x = None
    index = None
    for p_i, p in enumerate(points):
        if min_x:
            if p[0] < min_x:
                min_x = p[0]
                min_point = p
                if indicies:
                    index = indicies[p_i]
        else:
            min_x = p[0]
            min_point = p
            if indicies:
                index = indicies[p_i]
    if indicies:
        return min_point, index
    else:
        return min_point

def min_point_y(points, indicies=None):
    '''
    calculates the point in points with minimum y value
    if `indicies` is specified, the index of the point is also returned
    '''
    min_y = None
    index = None
    for p_i, p in enumerate(points):
        if min_y:
            if p[1] < min_y:
                min_y = p[1]
                min_point = p
                if indicies:
                    index = indicies[p_i]
        else:
            min_y = p[1]
            min_point = p
            if indicies:
                index = indicies[p_i]
    if indicies:
        return min_point, index
    else:
        return min_point

def sort_polar_angle(points, minPoint):
    """
    [Function taken from the convex hull lab code]
    Sort a set of points (in ascending order) based on their polar angles.
    Input:
        points <'list'>    - A set of points in the form of x, y, label.
        minPoint <'Point'> - The point which has the minimum vertical coordinate (i.e., the most bottom point).
    Output:
        points_sorted <'list'> - The sorted points in the form of x, y, label.
    """
    points.remove(minPoint)

    # The polar angle is computed by 'theta = arctan(deltaY / deltaX)'.
    points.sort(key=lambda p: np.arctan2(p[1] - minPoint[1], p[0] - minPoint[0]))  # radian
    # points.sort(key=lambda p: np.arctan2(p[1] - minPoint[1], p[0] - minPoint[0]) * 180 / np.pi)  # degree

    points_sorted = [minPoint] + points

    return points_sorted


def remove_inner_point(points, minPoint):
    """
    [Function taken from the convex hull lab code]
    Remove the inner point of a set of sorted points that has the same polar angle with an outer point.
    Input:
        points <'list'>    - A set of sorted points in the form of x, y, label.
        minPoint <'Point'> - The point which has the minimum vertical coordinate (i.e., the most bottom point).
    Output:
        points_unique <'list'> - The sorted points in the form of x, y, label with unique polar angles.
    """
    p_min = minPoint
    p_all = points
    p_uni = [minPoint, points[1]]  # It should be 'points[1]' (i.e., the 2nd point in 'points') not 'points[0]'!

    for i in range(2, len(p_all)):  # Start with the 3rd point in 'points'!
        # Check if 'p_min p_all[i]' and 'p_min p_uni[-1]' have the same polar angle.
        # Check if 'p_all[i]' and 'p_uni[-1]' are collinear.
        if (p_min[1] - p_uni[-1][1]) * (p_min[0] - p_all[i][0]) == (p_min[1] - p_all[i][1]) * (p_min[0] - p_uni[-1][0]):
            # If true, check which point has greater vertical coordinate (i.e., the outer point).
            if abs(p_uni[-1][1]) < abs(p_all[i][1]):
                # Remove the inner point and add the outer point.
                p_uni.remove(p_uni[-1])
                p_uni.append(p_all[i])  # Go to check the next point in 'points'.
            continue  # Continue the for loop!
        else:
            p_uni.append(p_all[i])  # Go to check the next point in 'points'.

    points_unique = p_uni

    return points_unique

def cw_turn(p1, p2, p3):
    """
    [Function taken from the convex hull lab code]
    Check if the orientation of three points (p1, p2, p3) is clockwise (CW).
    Input:
        p1 <'Point'> - The 1st point in the form of x, y, label.
        p2 <'Point'> - The 2nd point in the form of x, y, label.
        p3 <'Point'> - The 3rd point in the form of x, y, label.
    Output:
        if_cw <'bool'> - If True, the orientation of those three points is CW.
    """
    turn = (p2[0] - p1[0]) * (p3[1] - p2[1]) - (p2[1] - p1[1]) * (p3[0] - p2[0])

    if_cw = round(turn, 4) < 0  # The 'round()' function is needed to avoid floating point error.

    return if_cw

def sign(p1, p2, p3):
    return (p1[0]-p3[0])*(p2[1]-p3[1]) - (p2[0]-p3[0])*(p1[1]-p3[1])

def point_in_trangle(p, t1, t2, t3):
    '''
    returns true if p lies within the triangle (t1,t2,t3)
    uses barycentric coordinates
    '''
    b1 = sign(p, t1, t2)
    b2 = sign(p, t2, t3)
    b3 = sign(p, t3, t1)

    negative = b1 < 0 or b2 < 0 or b3 < 0
    posistive = b1 > 0 or b2 > 0 or b3 > 0
    return not negative or not posistive

def corners(points, indicies):
    '''
    calculates the most extreme points, used as a
    starting simplex for the quickhull algorithm
    '''
    min_x = min_point_x(points, indicies)[1]
    max_x = min_point_x([(-p[0],-p[1]) for p in points], indicies)[1]
    min_y = min_point_y(points, indicies)[1]
    max_y = min_point_y([(-p[0],-p[1]) for p in points], indicies)[1]
    return [min_x, max_y, max_x, min_y]