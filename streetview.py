# Import google_streetview for the api module
import google_streetview.api
import math

keys=[]
def get_image(lat, lon, head):
    # Define parameters for street view api
    params = [{
    	'size': '640x640', # max 640x640 pixels
    	'location':  str(lat)+","+str(lon),
    	'heading': str(head),
    	'pitch': '-0.76',
    	'key': 'AIzaSyB_dSyepNFhGPDbNvrzn3yJmT3O1MpSldU'
    }]
    
    # Create a results object
    results = google_streetview.api.results(params)
    
    # Download images to directory 'downloads'
    results.download_links('downloads')
    keys.append((lat,lon))
    
streets= [ [(40.819283, -73.910595), (40.821256, -73.909943)] , 
            [(40.821256, -73.909943), (40.821497, -73.911144)], 
            [(40.821497, -73.911144), (40.820281, -73.911885)], 
            [(40.820281, -73.911885), (40.818023, -73.913214)], 
            [(40.818023, -73.913214),(40.816310, -73.914167)],
            [(40.816310, -73.914167),(40.816180, -73.911897)],
            [(40.816180, -73.911897),(40.819039, -73.910700)]
            ]
steps = 7

for i in streets:
    m = (i[1][0]-i[0][0]), (i[1][1]-i[0][1])
    head = math.atan( m[0]/ m[1] )*(180/math.pi)+180
    get_image(i[0][0],i[0][1], head)
    
    for l in range(1, steps-1):
        get_image(i[0][0]+m[0]*(l/(steps-1)), i[0][0]+m[1]*(l/(steps-1)), head)
        
    get_image(i[1][0],i[1][1], head)

print(keys)