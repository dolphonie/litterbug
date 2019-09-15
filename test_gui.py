import random as r
import matplotlib.pyplot as plt
# %matplotlib notebook

# map_file = "map.png"
# trash_file = "trash.png"
# master = tk.Tk()
# whatever_you_do = "Whatever you do will be insignificant, but it is very important that you do it.\n(Mahatma Gandhi)"
# msg = tk.Message(master, text = whatever_you_do)
# msg.config(bg='lightgreen', font=('times', 24, 'italic'))
# msg.pack()
# tk.mainloop()

size = 20
#make nodes
nodes=[]
for x in range(size):
    for y in range(size):
        nodes.append([x+r.random(),y+r.random()])
nodes = [[round(x*50),round(y*50)] for [x,y] in nodes]
#make edges
edges=[]
for i in range(size):
    for j in range(size):
        if j != size-1:
            edges.append([j+20*i,j+20*i+1])
        if i != size-1:
            edges.append([j+20*i,j+20*(i+1)])

nodes_x, nodes_y = list(zip(*nodes))

#make litter
weights=[]
res = 4
for i in range(len(edges)):
    weights.append([])
    for j in range(res):
        if r.randint(0, 99) < 50:
            weights[i].append(0)
        else:
            weights[i].append(r.randint(0,5))

fig, ax = plt.subplots(figsize=(10, 10))
ax.scatter(nodes_x, nodes_y, zorder=3)
# plt.plot([122, 123], [644, 694], color='black')
for edge in edges:
    na, nb = edge
    ax.plot([nodes_x[na], nodes_x[nb]], [nodes_y[na], nodes_y[nb]], color='black')

print("Nodes: ")
print(nodes)
print("Edges: ")
print(edges)
print("Litter: ")
print(weights)


