

import numpy as np
import sys
# depth of recursion of raytraycing

MAX_depth = 3

"""
Read file that contains required components for raytraycing. ex) objects, background, light ect..
input: txt file
output: element for raytraycing in dictionary data type
"""
def read_file(file_name):
    multiple_element = ["SPHERE","LIGHT"]
    out_dict={}
    content_file = open(file_name,'r');
    for line in content_file:
        if line.split() != []:
            if line.split()[0] not in out_dict:
                if(line.split()[0] in multiple_element):
                    out_dict[line.split()[0]]=[[float(i) for i in line.split()[2:]]]
                else:
                    out_dict[line.split()[0]]=line.split()[1:]
            else:
                out_dict[line.split()[0]].append([float(i) for i in line.split()[2:]])
    content_file.close()
    return out_dict
"""
It will produce sphere objects components from parsing dictionary
data: dictionay from parsed file input
output: sphere components in dictionary format
"""
def get_objects(data):
    spheres = []
    for item in data['SPHERE']:
        sphere={}
        sphere['pos']=np.array([item[0],item[1],item[2]])
        sphere['scale']=np.matrix([[item[3],0,0],[0,item[4],0,],[0,0,item[5]]])
        sphere['trans'] = np.matrix([[item[3],0,0,item[0]],[0,item[4],0,item[1]],[0,0,item[5],item[2]],[0,0,0,1]])
        sphere['color'] = np.array([item[6],item[7],item[8]])
        sphere['ambient']=float(item[9])
        sphere['diffuse']=float(item[10])
        sphere['specular']=float(item[11])
        sphere['reflect']=float(item[12])
        sphere['specexp']=float(item[13])
        spheres.append(sphere)
    return spheres
"""
It will produce light's components from parsing dictionary
data: dictionay from parsed file input
output: light's components in dictionary format
"""
def get_lights(data):
    lights = []
    for item in data['LIGHT']:
        light={}
        light['pos']=np.array([item[0],item[1],item[2]])
        light['color'] = np.array([item[3],item[4],item[5]])
        lights.append(light)
    return lights
"""
Normalize a vector
"""
def normalize(vector):
    return vector / np.linalg.norm(vector)
"""
Find intersection point between ray and object
input: sphere: sphere's components
        ray_origin: camera location
        ray_direction: direction of ray
return: if ray hit the object, return distance
        between camera and objects
        else None
"""
def intersect(sphere,ray_origin,ray_direction):
    
    scale = sphere['scale']
    center = sphere['pos']
    #apply inverse transform
    ray_origin = ray_origin - center
    inverse_transp= np.linalg.inv(scale)
    ray_origin = np.dot(inverse_transp,ray_origin)
    ray_direction = np.dot(inverse_transp,ray_direction)
    ray_origin = np.squeeze(np.asarray(ray_origin))
    ray_direction = np.squeeze(np.asarray(ray_direction))
    #calculate normal of sphere
    a = np.dot(ray_direction,ray_direction)
    b = np.dot(ray_origin,ray_direction)
    c = np.dot(ray_origin,ray_origin)-1
    delta = b ** 2 - a * c
    if delta > 0:
        t1 = -b/a + np.sqrt(delta)/a
        t2 = -b/a - np.sqrt(delta)/a
        #only in case of positive two answer exist
        #return distance
        if t1>0 and t2>0:
            return min(t1,t2)
    return None
"""
get closest intersected objects from ray, and its' distance
input: objects: elements of objects
       ray_origin: origin of ray
       ray_direction: origin of ray direction
output: if hit, closest intersected object and its' distance
        else return None and the distance as infinity
"""
def closest_intersected_object(objects, ray_origin, ray_direction):
    #check every objects wheather it is intersected by ray or not
    distances = [intersect(obj, ray_origin, ray_direction) for obj in objects]
    nearest_object = None
    min_distance = np.inf
    for index, distance in enumerate(distances):
        if distance and distance < min_distance:
            min_distance = distance
            nearest_object = objects[index]
    return nearest_object, min_distance
"""
Main algorithm 
return vector of color
"""
def raytrace(origin,direction,depth,objects,background,lights,camera,reflection,default_ambient):
    # set initial color zero(black)
    color = np.zeros([3])
    # set depth of recursion. if ray reaches max depth return black
    if(depth>MAX_depth):
        return np.array([0,0,0])
    # get closest object, and its distance
    closest_object, min_distance = closest_intersected_object(objects, origin,direction)
    # if the ray hit nothing, then return background color for first time operating function
    # if the ray hit nothing after hit object, retun black
    if closest_object is None:
        if depth >0:
            return np.array([0,0,0])
        return background
    # get intersection point
    intersection = origin + min_distance * direction
    # to get normal apply inverse transepose
    inverse_transp= np.linalg.inv(closest_object['trans'].transpose())
    normal_to_surface = (intersection-closest_object['pos'])
    normal_to_surface = np.append(normal_to_surface,[1])
    normal_to_surface = np.dot(inverse_transp,normal_to_surface)
    normal_to_surface = np.squeeze(np.asarray(normal_to_surface))
    normal_to_surface = np.delete(normal_to_surface,[3])
    normal_to_surface = normalize(normal_to_surface)
    shifted_point = intersection + 1e-6 * normal_to_surface
    # apply local illumination
    # set initial variable for illumination as black
    illution = np.array([0.,0.,0.])
    # apply ambient
    ambient = closest_object['color']  * closest_object['ambient'] * default_ambient
    illution+=ambient
    # for illumination, apply all lights source
    for light in lights:
        # get object to light vector
        light_direction = normalize(light['pos']-shifted_point)
        # if the ray intersected from the intersection point to light position
        # then it's shadowed, so no illumination
        _,near_object_distance = closest_intersected_object(objects, shifted_point, light_direction)
        light_distance = np.linalg.norm(light['pos']-intersection)
        is_shadowed = False
        if(near_object_distance>0.1):
            is_shadowed = near_object_distance<light_distance
        # if not shadowed, then apply illumination
        if not is_shadowed:
            # get diffuse and specular
            L = normalize(light['pos'] -shifted_point);
            V = normalize(camera - shifted_point) 
            N = normal_to_surface
            R= 2*np.dot(N,L)*N-L
            lightDotNormal = max( np.dot(L, N), 0.0)
            diffuse = lightDotNormal * closest_object['color'] * closest_object['diffuse']*light['color']
            specular = pow( max(np.dot(R, V), 0.0), closest_object['specexp'] ) * closest_object['specular'] * light['color']#//; //Phong
            if( np.dot(L, N) < 0.0 ):
                specular = np.array([0.0, 0.0, 0.0])
            illution += (diffuse+specular)
    color += illution*reflection
    reflection *= closest_object['reflect']
    # get reflected color by doing recursing
    if reflection != 0:
        re_origin = shifted_point
        re_direction = direction-2*np.dot(direction,normal_to_surface)*normal_to_surface
        color += raytrace(re_origin,re_direction,depth+1,objects,background,lights,camera,reflection,default_ambient)
    return color

def main():
    # read input file and set environment
    data = read_file(sys.argv[1])
    objects = get_objects(data)
    lights = get_lights(data)
    ambient = np.array([float(i) for i in data['AMBIENT']])
    background = np.array([float(i) for i in data['BACK']])
    width = int(data['RES'][0])
    height = int(data['RES'][1])
    right = float(data['RIGHT'][0])
    left = float(data['LEFT'][0])
    bottom = float(data['BOTTOM'][0])
    top = float(data['TOP'][0])
    near =  float(data['NEAR'][0])
    camera = np.array([0,0,0])
    image = np.zeros((height, width, 3))
    for x in range(width):
        for y in range(height):
            # set screen coordinate
            uc = left + right*2*x/width
            vr = bottom + top*2*((height-1)-y)/height
            origin = camera
            color = np.zeros((3))
            direction = normalize(np.array([uc,vr,-near]))
            depth = 0
            reflection =1
            color = raytrace(origin,direction,depth,objects,background,lights,camera,reflection,ambient)
            image[x,y] = np.clip(color, 0, 1)
        print("%d/%d" % (x + 1, height))
    # generate ppm image
    f = open(data['OUTPUT'][0], "w")
    f.write("P3\n")
    f.write(str(width))
    f.write(" ")
    f.write(str(height))
    f.write("\n255\n")
    for y in range(height):
        if not y == height-1:
            f.write(" ")
        for x in range(width):
            for i in range(3):
                f.write(str(int(image[x][y][i]*255)))
                f.write("  ")
            f.write("  ")
        f.write("\n")
    f.close()
main()
