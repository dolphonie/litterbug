
# coding: utf-8

# In[93]:


from collections import defaultdict
from sklearn.cluster import KMeans
import numpy as np
import matplotlib.pyplot as plt
# get_ipython().run_line_magic('matplotlib', 'notebook')


# In[70]:


# Algorithms
def Bresenham(x0, y0, x1, y1):
    """
    Given two x,y coords (x0, y0), (x1, y1), return
    a list of (x,y) cells on the straight line between them
    inclusive of the end coords.
    """
    output = []
    dx = abs(x1 - x0)
    sx = 1 if x0 < x1 else -1
    dy = -abs(y1 - y0)
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        output.append((x0, y0))
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy
    return output

def FloydWarshall(m):
    """
    Given a map, return an array of distances between nodes
    """
    n_v = len(m.nodes)
    dist = np.full((n_v, n_v), np.inf)
    for n1, n2 in m.edges:
        dist[n1.id, n2.id] = ((n2.y - n1.y)**2 + (n2.x - n1.x)**2)**0.5
        dist[n2.id, n1.id] = ((n2.y - n1.y)**2 + (n2.x - n1.x)**2)**0.5
    for v in m.nodes:
        dist[v, v] = 0
    for k in range(n_v):
        for i in range(n_v):
            for j in range(n_v):
                if dist[i, j] > dist[i, k] + dist[k, j]:
                    dist[i, j] = dist[i, k] + dist[k, j]
    return dist


# In[77]:


class Map:
    def __init__(self, max_x, max_y):
        self.nodes = {}
        self.edges = set()
        self.cells = {}
        self.bounds = (max_x, max_y)
        self.node_dists = None
        self.dists = {}
        
    def add_node(self, x, y):
        n = (max(self.nodes) if len(self.nodes) else -1) + 1
        self.nodes[n] = MapNode(n, x, y)
        
    def add_edge(self, na, nb):
        n1, n2 = self.nodes[na], self.nodes[nb]
        self.edges.add((n1, n2))
        for x, y in Bresenham(n1.x, n1.y, n2.x, n2.y):
            if (x, y) not in self.cells:
                self.cells[(x, y)] = Cell(x, y, (n1, n2))
                
    def set_vals(self, trash=None, people=None):
        max_x, max_y = self.bounds
        if trash is None:
            trash = np.zeros((max_y, max_x))
        if people is None:
            people = np.zeros((max_y, max_x))
        for x in range(max_x):
            for y in range(max_y):
                if (x, y) in self.cells:
                    self.cells[(x, y)].set_values(trash[y, x], people[y, x])
                    
    def get_node_dists(self):
        self.node_dists = FloydWarshall(self)
        
    def get_dist(self, c1, c2):
        if (c1, c2) in self.dists:
            return self.dists[(c1, c2)]
        if (c2, c1) in self.dists:
            return self.dists[(c2, c1)]
        if self.node_dists is None:
            self.get_node_dists()
        edge1, edge2 = c1.edge, c2.edge
        if edge1 == edge2:
            dist = ((c2.y - c1.y)**2 + (c2.x - c1.x)**2)**0.5
        else:
            dist = float('inf')
            for nodeA in edge1:
                for nodeB in edge2:
                    node_dist = self.node_dists[nodeA.id, nodeB.id]
                    distA = ((c1.y - nodeA.y)**2 + (c1.x - nodeA.x)**2)**0.5
                    distB = ((c2.y - nodeB.y)**2 + (c2.x - nodeB.x)**2)**0.5
                    new_dist = node_dist + distA + distB
                    dist = min(dist, new_dist)
        self.dists[(c1, c2)] = dist
        return dist


# In[78]:


class MapNode:
    def __init__(self, n, x, y):
        self.id = n
        self.x = x
        self.y = y


# In[79]:


class Cell:
    def __init__(self, x, y, edge):
        self.x = x
        self.y = y
        self.edge = edge
        self.trash, self.people = 0, 0
    
    def set_values(self, trash=0, people=0):
        self.trash = trash
        self.people = people


# In[169]:


def PlaceOneTrashCan(m, cells=None, c=0.3):
    if cells is None:
        cells = [i for i, n in m.cells.items() if n.trash > 0]
    cells = [tuple(i) for i in cells]
    best_pos = (None, None)
    best_score = -float('inf')
    for cell_pos in cells:
        cell = m.cells[cell_pos]
        score = cell.people
        for cp2 in cells:
            cell2 = m.cells[cp2]
            cell_dist = m.get_dist(cell, cell2)
            score -= c * cell_dist * cell2.trash
        if score > best_score:
            best_score = score
            best_pos = cell_pos
    return best_pos, best_score


# In[209]:


def PlaceTrashCans(m, trash_cost=5):
    k = 1
    best_pos = None
    best_score = -float('inf')
    
    important_cells = [(i, n.trash) for i, n in m.cells.items()]
    important_cells, cell_trash = list(zip(*important_cells))
    X = np.array(important_cells).reshape(len(important_cells), 2)
    
    while True:
        trash_cans = []
        score = -k * trash_cost
        
        km = KMeans(n_clusters=k)
        predict = km.fit_predict(X, cell_trash)
        for i in range(k):
            cluster = X[predict == i].tolist()
            pos, sc = PlaceOneTrashCan(m, cluster)
            score += sc
            trash_cans.append(pos)
        
        if score > best_score:
            best_score = score
            best_pos = trash_cans
            k += 1
        else:
            return best_pos


# In[245]:


def Run(nodes, edges, trash_array, people_array):
    m = Map(max([i[0] for i in nodes]), max([i[1] for i in nodes]))

    # initializing
    for node in nodes:
        m.add_node(*node)
    for edge in edges:
        m.add_edge(*edge)
    m.set_vals(trash, people)
    m.get_node_dists()
    
    trash_pos = PlaceTrashCans(m)
    
    fig, ax = plt.subplots()
    ax.imshow(trash_array, cmap="hot")
    for edge in m.edges:
        ax.plot([edge[0].x, edge[1].x], [edge[0].y, edge[1].y], color='black')
    # ax.scatter(*zip(*important_cells), zorder=3)
    ax.scatter(*zip(*trash_pos), zorder=4)
    return trash_pos


# In[246]:


# Testing
nodes_x = [0, 3, 3, 5, 7, 0, 3, 5, 0, 3]
nodes_y = [0, 0, 4, 4, 4, 6, 6, 6, 7, 7]
nodes = list(zip(nodes_x, nodes_y))
edges = [(0, 1), (1, 2), (2, 3), (3, 4), (2, 6), (3, 7), (4, 7),
         (5, 6), (6, 7), (5, 8), (6, 9), (7, 9), (8, 9)]
trash = np.array([[0., 2., 3., 1., 0., 0., 0., 0.],
                  [0., 0., 0., 2., 0., 0., 0., 0.],
                  [0., 0., 0., 0., 0., 0., 0., 0.],
                  [0., 0., 0., 0., 0., 0., 0., 0.],
                  [0., 0., 0., 1., 2., 3., 1., 1.],
                  [0., 0., 0., 2., 0., 0., 3., 0.],
                  [2., 4., 0., 4., 1., 0., 0., 0.],
                  [4., 2., 2., 3., 0., 0., 0., 0.]])

people = np.array([[0., 1., 1., 1., 0., 0., 0., 0.],
                   [0., 0., 0., 1., 0., 0., 0., 0.],
                   [0., 0., 0., 2., 0., 0., 0., 0.],
                   [0., 0., 0., 3., 0., 0., 0., 0.],
                   [0., 0., 0., 1., 2., 1., 1., 3.],
                   [0., 0., 0., 2., 0., 1., 2., 0.],
                   [3., 2., 2., 3., 1., 1., 0., 0.],
                   [3., 2., 1., 4., 2., 0., 0., 0.]])

print(Run(nodes, edges, trash, people))

