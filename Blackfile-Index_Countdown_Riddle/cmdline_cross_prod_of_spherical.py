#Writen by TH3EEuphoricFan1161
import argparse
import math


#================================================#
#                    Argparse                    #
#================================================#
parser = argparse.ArgumentParser()
parser.add_argument("-c1", "--coordinates1", type=str, default=None, help='Enter Earth coordinates as "(lat,long)" with the ""s and no spaces!')
parser.add_argument("-c2", "--coordinates2", type=str, default=None, help='Enter Earth coordinates as "(lat,long)" with the ""s and no spaces!')
parser.add_argument("-v", "--verbose", action="store_true", help='Verbose printing')
parser.add_argument("-i", "--interesting", action="store_true", help='(Lat,Long) I find interesting and why')
parser.add_argument("-ic", "--interesting_coordinates", action="store_true", help='Run all interesting coordinate pairs in one go, overrides input coordinates')
args = parser.parse_args()


#===============================================#
#            My Interesting Locations           #
#===============================================#
pre_def_coords = []
pre_def_coords.append("(63.77773527749968,-171.73267990336026)")
pre_def_coords.append("(63.6938293157767,-170.48335927373108)")
#Thrown out since the riddle states a singluar island: "an island"
#pre_def_coords.append("(56.60162221716144,-169.54865466530055)")
#pre_def_coords.append("(57.12074737564973,-170.282875912858)")


#===============================================#
#                   Functions                   #
#===============================================#
def my_interesting_locations():
    print("===========================================================================================================")
    print("Moshi Moshi!  Here are a list of coordinates I find interesting and why")
    print("|      Latitude        |      Longitude      |      Reasoning")
    print("+----------------------+---------------------+-------------------------------------------------------------")
    print(f"| {63.77773527749968}    | {-171.73267990336026} | Gambell on St. Lawrence Island 'two ivory towns' ")
    print("+----------------------+---------------------+-------------------------------------------------------------")
    print(f"| {63.6938293157767}     | {-170.48335927373108} | Savoonga on St. Lawrence Island 'two ivory towns' ")
    print("+----------------------+---------------------+-------------------------------------------------------------")
    #Thrown out since the riddle states a singluar island: "an island"
    #print(f"| {56.60162221716144}    | {-169.54865466530055} | St. George on St. George Island 'two ivory towns' ")
    #print("+----------------------+---------------------+-------------------------------------------------------------")
    #print(f"| {57.12074737564973}    | {-170.282875912858}   | St. Paul on St. Paul Island 'two ivory towns' ")
    #print("+----------------------+---------------------+-------------------------------------------------------------")

def cross_product(v1, v2):
    vx = v1[1]*v2[2] - v1[2]*v2[1]
    vy = -v1[0]*v2[2] + v1[2]*v2[0]
    vz = v1[0]*v2[1] - v1[1]*v2[0]
    v = [vx, vy, vz]
    return v

def convert_sph_to_cart(v):
    #<r, theta, phi> ==> <x, y, z>
    x = v[0]*math.cos(v[1])*math.cos(v[2])
    y = v[0]*math.sin(v[1])*math.cos(v[2])
    z = v[0]*math.sin(v[2])
    v_cart = [x, y, z]
    return v_cart

def convert_cart_to_sph(v):
    #<x, y, z> ==> <r, theta, phi>
    r = math.sqrt(math.pow(v[0],2) + math.pow(v[1],2) + math.pow(v[2],2))
    phi = math.asin(v[2]/r)
    theta = math.atan2(v[1], v[0]) #same as arctan(y/x) but without ambiguity in the result's sign (thanks to @tylerginn_ in the discord for the suggestion)
    v_sph = [r, theta, phi]
    return v_sph

def parse_in_to_sph(coord_str):
    lat_long = coord_str[1:-1].split(",")
    v_sph = [1, lat_long[1], lat_long[0]]
    return v_sph

def convert_sph_vec_to_RAD(v):
    v[1] = float(v[1])*math.pi/180
    v[2] = float(v[2])*math.pi/180
    return v

def convert_sph_vec_to_DEG(v):
    v[1] = float(v[1])*180/math.pi
    v[2] = float(v[2])*180/math.pi
    return v

def convert_lat_long_to_MC(lat, long):
    print(f"\n=============  Now converting ({lat},{long}) to MC coordinates  =============")
    print("Here assume 'raising' is addition on latitude and 'just twice' is squaring")
    x = float(long)*float(long)
    z = float(lat)+63
    print(f"({x},{z})")
    print("And rounding down to follow the riddle results in:")
    mc_x = math.floor(x)
    mc_z = math.floor(z)
    print(f"    ========>  X = {mc_x}, Z = {mc_z}  <========    ")

def handle_code(coords1, coords2, is_verbose):
    c_1 = parse_in_to_sph(coords1)
    c_2 = parse_in_to_sph(coords2)
    print(f"You entered (lat={c_1[2]}, long={c_1[1]}) and (lat={c_2[2]}, long={c_2[1]})")
    c_1 = convert_sph_vec_to_RAD(c_1)
    c_2 = convert_sph_vec_to_RAD(c_2)
    if is_verbose:
        print(f"Which in sphereical is: <{c_1[0]}, {c_1[1]}, {c_1[2]}> and <{c_2[0]}, {c_2[1]}, {c_2[2]}>")
    v_1 = convert_sph_to_cart(c_1)
    v_2 = convert_sph_to_cart(c_2)
    if is_verbose:
        print(f"These convert to cartesian: <{v_1[0]}, {v_1[1]}, {v_1[2]}> and <{v_2[0]}, {v_2[1]}, {v_2[2]}>")
    v_3 = cross_product(v_1, v_2)
    if is_verbose:
        print(f"The resulting cross product is: <{v_3[0]}, {v_3[1]}, {v_3[2]}>")
    c_3 = convert_cart_to_sph(v_3)
    if is_verbose:
        print(f"Converting back to spherical: <{c_3[0]}, {c_3[1]}, {c_3[2]}>")
    l_3 = convert_sph_vec_to_DEG(c_3)
    
    v_4 = cross_product(v_2, v_1)
    if is_verbose:
        print(f"Flipping the input order, the resulting cross product is: <{v_4[0]}, {v_4[1]}, {v_4[2]}>")
    c_4 = convert_cart_to_sph(v_4)
    if is_verbose:
        print(f"Converting back to spherical: <{c_4[0]}, {c_4[1]}, {c_4[2]}>")
    l_4 = convert_sph_vec_to_DEG(c_4)

    print("Giving:")
    print(f"  (lat={l_3[2]}, long={l_3[1]})  with  r = {c_3[0]} R_Earth \n      For quick copy-paste to google maps: {l_3[2]} {l_3[1]}")
    print(f"  (lat={l_4[2]}, long={l_4[1]})  with  r = {c_4[0]} R_Earth \n      For quick copy-paste to google maps: {l_4[2]} {l_4[1]}")

    convert_lat_long_to_MC(l_3[2], l_3[1])
    convert_lat_long_to_MC(l_4[2], l_4[1])


#===============================================#
#                    "Main"                     #
#===============================================#
if args.interesting:
    my_interesting_locations()

if args.coordinates1 is not None and args.coordinates2 is not None and args.interesting_coordinates is not True:
    print("===========================================================================================================")
    print("Using units where the radius of the Earth R_Earth := 1 (arbitrary when only extracting lat and long)")
    print("Using spherical coordinate convention where \u0398 := Longitude and \u03C6 := Latitude")
    print("===========================================================================================================")
    handle_code(args.coordinates1, args.coordinates2, args.verbose)
    print("===========================================================================================================")
if args.interesting_coordinates:
    print("===========================================================================================================")
    print("Running all of the coordinate pairs I find interesting in one go...")
    print("Using units where the radius of the Earth R_Earth := 1 (arbitrary when only extracting lat and long)")
    print("Using spherical coordinate convention where \u0398 := Longitude and \u03C6 := Latitude")
    print("===========================================================================================================")
    handle_code(pre_def_coords[0], pre_def_coords[1], args.verbose) #Proximity of towns (same island)
    print("\n===========================================================================================================")


print("But it was me... Diomede!")
