
# coding: utf-8

# In[94]:


from collections import defaultdict
from sklearn.cluster import KMeans
import skimage.measure
import numpy as np
import random as r
import matplotlib.pyplot as plt
# get_ipython().run_line_magic('matplotlib', 'notebook')


# In[2]:


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


# In[3]:


class Map:
    def __init__(self, max_x, max_y):
        self.nodes = {}
        self.edges = set()
        self.cells = {}
        self.bounds = (max_x, max_y)
        self.node_dists = None
        self.dists = {}
        self.filtered_cells = []
        
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

    def filter_cells(self):
        self.filtered_cells = [z for z, cell in self.cells.items() if cell.trash > 0]
                    
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


# In[4]:


class MapNode:
    def __init__(self, n, x, y):
        self.id = n
        self.x = x
        self.y = y


# In[5]:


class Cell:
    def __init__(self, x, y, edge):
        self.x = x
        self.y = y
        self.edge = edge
        self.trash, self.people = 0, 0
    
    def set_values(self, trash=0, people=0):
        self.trash = trash
        self.people = people


# In[6]:


def PlaceOneTrashCan(m, cells=None, c=0.3):
    if cells is None:
        cells = m.filtered_cells
    cells = [tuple(i) for i in cells]
    best_pos = (None, None)
    best_score = -float('inf')
    for cell_pos, cell in m.cells.items():
        score = cell.people
        for cp2 in cells:
            cell2 = m.cells[cp2]
            cell_dist = m.get_dist(cell, cell2)
            score -= c * cell_dist * cell2.trash
        if score > best_score:
            best_score = score
            best_pos = cell_pos
    return best_pos, best_score


# In[106]:


def PlaceTrashCans(m, trash_cost=5):
    k = 1
    best_pos = None
    best_score = -float('inf')
    
    important_cells = m.filtered_cells
    cell_trash = [m.cells[i].trash for i in important_cells]
    X = np.array(important_cells).reshape(len(important_cells), 2)
    
    while True:
        print(k)
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


# In[122]:


def Run(nodes, edges, trash_array, people_array, save_name, trash_cost=5):
    print("Running")
    m = Map(max([i[0] for i in nodes]), max([i[1] for i in nodes]))

    # initializing
    for node in nodes:
        m.add_node(*node)
    print("created nodes")
    for edge in edges:
        m.add_edge(*edge)
    print("created graph")
    m.set_vals(trash_array, people_array)
    print("set vals")
    m.get_node_dists()
    print("got distances")
    m.filter_cells()
    print("filtered down to", len(m.filtered_cells), "/", len(m.cells))
    trash_pos = PlaceTrashCans(m, trash_cost=trash_cost)
    
    fig, ax = plt.subplots()
    
    sr = trash_array.shape[0] // 100 + 1
    trash = skimage.measure.block_reduce(trash_array, (sr, sr), np.max).repeat(sr, axis=0).repeat(sr, axis=1)
    plt.imshow(trash, cmap='hot')
    for edge in m.edges:
        ax.plot([edge[0].x, edge[1].x], [edge[0].y, edge[1].y], color='black')
    # ax.scatter(*zip(*important_cells), zorder=3)
    ax.scatter(*zip(*trash_pos), zorder=4)
    fig.savefig(save_name)
    return len(trash_pos), trash_pos


# In[126]:

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
                  [0., 0., 0., 1., 2., 3., 1., 3.],
                  [0., 0., 0., 2., 0., 0., 3., 0.],
                  [2., 4., 0., 4., 1., 0., 0., 0.],
                  [4., 2., 2., 3., 0., 0., 0., 0.]])

test1 = Run(nodes, edges, trash, None, "test1", 3.5)
print(test1)

fig, ax = plt.subplots()
plt.imshow(trash, cmap='hot')
for edge in edges:
    ax.plot([nodes_x[edge[0]], nodes_x[edge[1]]], [nodes_y[edge[0]], nodes_y[edge[1]]], color='b', linewidth=1, alpha=0.5)
ax.scatter(*zip(*(test1[1])), zorder=4, color='g')
fig.savefig("test1.png")


# Big test
size = 15
#make nodes
nodes=[]
for x in range(size):
    for y in range(size):
        nodes.append([x+0.5*r.random(),y+r.random()])
nodes = [[round(x*25),round(y*25)] for [x,y] in nodes]
nodes_x, nodes_y = list(zip(*nodes))
#make edges
edges=[]
for i in range(size):
    for j in range(size):
        if j != size-1:
            edges.append([j+15*i,j+15*i+1])
        if i != size-1:
            edges.append([j+15*i,j+15*(i+1)])
#make litter
weights=[]
res = 4
for i in range(len(edges)):
    weights.append([])
    for j in range(res):
        if r.randint(0, 99) < 60:
            weights[i].append(0)
        else:
            weights[i].append(r.randint(0,8))


# In[127]:


trash = np.zeros((size * 25 + 1, size * 25 + 1))
for i in range(len(edges)):
    edge = edges[i]
    na, nb = edge
    path = Bresenham(nodes_x[na], nodes_y[na], nodes_x[nb], nodes_y[nb])
    section_length = len(path) // 3
    trash[path[0][::-1]] = weights[i][0]
    trash[path[section_length][::-1]] = weights[i][1]
    trash[path[section_length*2][::-1]] = weights[i][2]
    trash[path[-1][::-1]] = weights[i][3]

test2 = Run(nodes, edges, trash, None, "test2", 30)
print(test2)

# Display

trash = np.zeros((size * 25 + 1, size * 25 + 1))
for i in range(len(edges)):
    edge = edges[i]
    na, nb = edge
    path = Bresenham(nodes_x[na], nodes_y[na], nodes_x[nb], nodes_y[nb])
    section_length = len(path) // 3
    trash_weights = np.concatenate([np.linspace(weights[i][0], weights[i][1], section_length),
                    np.linspace(weights[i][1], weights[i][2], section_length),
                    np.linspace(weights[i][2], weights[i][3], section_length),
                    np.full((len(path) % 3 + 1), weights[i][-1])])
    for i, (x, y) in enumerate(path):
        trash[y, x] = trash_weights[i]


sr = 8
trash1 = skimage.measure.block_reduce(trash, (sr, sr), np.max).repeat(sr, axis=0).repeat(sr, axis=1)

fig, ax = plt.subplots()
plt.imshow(trash1, cmap='hot')
for edge in edges:
    ax.plot([nodes_x[edge[0]], nodes_x[edge[1]]], [nodes_y[edge[0]], nodes_y[edge[1]]], color='#37FDFC', linewidth=2, alpha=0.5)
ax.scatter(*zip(*(test2[1])), s=150, zorder=4, color='#66ff00', edgecolors='black')
fig.savefig("test3.png")

