# Import google_streetview for the api module
import google_streetview.api
import math
import os
from matplotlib import pyplot as plt
coordx=[]
coordy=[]
hist=[]

search = True
steps = 3
#3 points to define rectangle
#p1------p2
#        |
#       p3
p1 = 40.743323, -74.011172#localization point
p3 = 40.783232, -73.944713
p2 = 40.795299, -73.973228 #corner point
height = 10 #blocks
width = 82
#14ths street to 96th street

slopex = (p2[0]-p1[0])/width,(p2[1]-p1[1])/width #width basis and 
slopey = (p3[0]-p2[0])/height,(p3[1]-p2[1])/height #height basis


nodes=[]
for y in range(height):
    for x in range(width):
        nodes.append((p1[0]+slopex[0]*x+slopey[0]*y, p1[1]+slopex[1]*x+slopey[1]*y))
#make edges
edges=[]
for y in range(height-1):
    for x in range(width-1):
        edges.append([x+width*y,x+width*y+1])
        edges.append([x+width*y,x+width*(y+1)])


def get_image(lat, lon, head, edge_id):
    # Define parameters for street view api
    coordx.append(lat)
    coordy.append(lon)
    if search:
        params = [{
        	'size': '640x640', # max 640x640 pixels
        	'location':  str(lat)+","+str(lon),
        	'heading': str(head),
        	'pitch': '-0.76',
        	'key': 'AIzaSyDhPefszM5msxfXW6XM9FwxqmbjQ-MVLN4'
        }]
        # Create a results object
        results = google_streetview.api.results(params)
        # Download images to directory 'downloads'
        results.download_links('downloads')
        #rename file
        name = str(round(lat*100000))+"_"+str(round(lon*100000))+"_"+str(edge_id)
        dst = name + ".jpg"
        src ='downloads/'+ 'gsv_0.jpg' 
        dst ='downloads/'+ dst 
        try:
            os.rename(src, dst) 
            print("Success")
        except:
            print("Failed to rename")
    
def scan():
    for e in range(len(edges)):
        i=[nodes[edges[e][0]],nodes[edges[e][1]]]
        hist.append(i)
        m = (i[1][0]-i[0][0]), (i[1][1]-i[0][1])
        head = math.atan( m[1]/ m[0] )*(180/math.pi)+90
        get_image(i[0][0],i[0][1], head, e)
        
        for l in range(1, steps-1):
            get_image(i[0][0]+m[0]*(l/(steps-1)), i[0][1]+m[1]*(l/(steps-1)), head, e)
            
        get_image(i[1][0],i[1][1], head, e)
        
        
#Run once
scan()
plt.scatter(coordx,coordy, s=2)
plt.show()