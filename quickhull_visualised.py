import os
import subprocess

import math
import random
import time

import matplotlib.pyplot as plt

from utils import cw_turn, corners, point_in_trangle

# generate random points
POINT_COUNT = 1024
X_RANGE = 100
Y_RANGE = X_RANGE
BUFFER = 2
SAVE_STEPS = True


def plot_points(points, polygon_verts, filename, labels=False):
    """plot the points and the polygon determined by the list
       of indicies, saves to file"""
    fig = plt.figure()
    ax = fig.add_subplot(111)

    # all points
    plt.plot([p[0] for p in points], [p[1] for p in points], '. k', markersize=4)
    # polygon lines
    plt.plot([points[p][0] for p in polygon_verts],[points[p][1] for p in polygon_verts],'#16161d')
    # polygon verticies
    plt.plot([points[p][0] for p in polygon_verts],[points[p][1] for p in polygon_verts], '. r', markersize=4)
    
    #if len(points) <= max(polygon_verts):
    #    print('error')
    plt.xlim([-X_RANGE-BUFFER,X_RANGE+BUFFER])
    plt.ylim([-Y_RANGE-BUFFER,Y_RANGE+BUFFER])
    plt.axis('off')

    if labels:
        for i, p in enumerate(points):
            ax.annotate(str(i), xy=p)

    if filename=="":
        ValueError("filename_id cannot be empty")
    else:
        plt.savefig(f'out/{filename}.png')
    #plt.show()
    plt.close()

def remove_indicies_in_triangle(points, indicies, i_1, i_2, i_3):
    '''removes indicies relating to points that are inside
       the triangle formed by i_1, i_2, and i_3'''
    return list(filter(lambda i: not point_in_trangle(points[i],points[i_1],points[i_2],points[i_3]),indicies))

def subset_outside_line(points, indicies, i_1, i_2):
    '''creates a subset of indicies that are outside the
       line formed by i_1 and i_2'''
    return list(filter(lambda i: cw_turn(points[i_1],points[i],points[i_2]),indicies))

def area(p1, p2, p3):
    '''calculates the area of the triangle formed by p1, p2, and p3'''
    v1 = (p2[0]-p1[0],p2[1]-p1[1])
    v2 = (p3[0]-p1[0],p3[1]-p1[1])
    return (v1[0]*v2[1] - v1[1]*v2[0])/2

def extend_edge(edge, points, subset_indicies, steps):
    '''recursively adds the furthest point from the edge
       (within the provided subset) to the hull'''
    hull = edge
    subset_indicies = list(filter(lambda p: area(points[p],points[edge[0]],points[edge[1]])>0,subset_indicies))
    if len(subset_indicies)==0:
        return hull, steps
    else:
        # choose largest area
        subset_indicies.sort(key=lambda p: area(points[p],points[edge[0]],points[edge[1]]), reverse=True)
        hull = [hull[0], subset_indicies[0], hull[1]]
        new_subset_indicies = remove_indicies_in_triangle(points, subset_indicies, hull[0], hull[1], hull[2])
        steps.append(hull.copy())
        #
        prev_steps_len = len(steps)
        out_1, steps = extend_edge((hull[0],hull[1]), points, new_subset_indicies, steps)
        for k in range(prev_steps_len, len(steps)):
            steps[k] = steps[k] + hull[1:3]
        #
        prev_steps_len = len(steps)
        out_2, steps = extend_edge((hull[1],hull[2]), points, new_subset_indicies, steps)
        for k in range(prev_steps_len, len(steps)):
            steps[k] = list(out_1)+steps[k]
        return out_1[:-1] + out_2, steps

def quickhull(points):
    '''with the limiting points (max/min x/y), extend the
       created edges to form the convex hull'''
    point_indicies = list(range(len(points)))
    c_i = list(dict.fromkeys(corners(points, point_indicies))) # remove duplicates
    steps = [c_i+[c_i[0]]]
    
    # removes any points inside the simplex defined by points in c_i
    if len(c_i) > 2:
        point_indicies = remove_indicies_in_triangle(points, point_indicies, c_i[0], c_i[1], c_i[2])
    if len(c_i) > 3:
        point_indicies = remove_indicies_in_triangle(points, point_indicies, c_i[0], c_i[2], c_i[3])

    edges = [(c_i[i],c_i[(i+1)%len(c_i)]) for i in range(len(c_i))]
    hull = []
    for e in edges:
        #print('LOOP')
        #print('edge:'+str(e))
        point_indicies_subset = subset_outside_line(points, point_indicies, e[0], e[1])
        #print('subset: '+ str(point_indicies_subset))
        prev_steps_len = len(steps)
        e_, steps = extend_edge(e, points, point_indicies_subset, steps)
        for i in range(prev_steps_len, len(steps)):
            steps[i] = hull+steps[i]
        #print('final edge: '+str(e_))
        hull += e_[:-1]

    return points, hull, steps

if __name__=='__main__':
    points = []
    # generate a cloud of random points
    for i in range(POINT_COUNT):
        # uniform square distribution is used for this demonstation
        x = random.randint(-X_RANGE,X_RANGE)
        y = random.randint(-Y_RANGE,Y_RANGE)
        
        if (x,y) not in points:
            points.append((x,y))

    t_start = time.time()
    points, final_hull, steps = quickhull(points)
    t_delta = time.time() - t_start
    print(f'Hull calculated using Quickhull algorithm in {t_delta:0.10f}s')
    print(f'Points in produced hull: {[points[i] for i in final_hull]}')
    #print(len(steps))

    final_hull = final_hull + [final_hull[0]]

    os.makedirs('out', exist_ok=True)
    if SAVE_STEPS==True:
        n = math.ceil(math.log(len(steps)+0.1, 10))
        # draw steps
        for i in range(len(steps)):
            plot_points(points, steps[i], f'graph_step{str(i).zfill(n)}')
        plot_points(points, final_hull, f'graph_step{str(len(steps)).zfill(n)}')
    # draw full convex hull
    plot_points(points, final_hull, 'final_hull')
    
    try:
        subprocess.run(f'cd out && ffmpeg -y -f image2 -r 3 -i graph_step%0{n}d.png -vcodec mpeg4 -b 800k video.avi',
                       shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        print('cannot compile animation: ffmpeg not installed')
