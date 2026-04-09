#Writen by TH3EEuphoricFan1161
import argparse


#================================================#
#                    Argparse                    #
#================================================#
parser = argparse.ArgumentParser()
parser.add_argument("-lat", "--latitude", type=str, default=None, help='Enter Earth latitude in deg as the integer rounding down')
parser.add_argument("-long", "--longitude", type=str, default=None, help='Enter Earth longitude in deg as the integer rounding down')
parser.add_argument("-y", "--y_value_in", type=str, default=None, help='Enter y value as a fraction of R_Earth')
args = parser.parse_args()


#================================================#
#    Define Functions for Coordinates ---> MC    #
#================================================#
def y_earth(y):
    return int(364 * float(y) - 64)

def option_1(lat, long):
    print("===========================================================================================================")
    print("Here assume 'raising' is addition on latitude and 'just twice' is addition:")
    print(f"({float(long)+2},{float(lat)+63})")

def option_2(lat, long):
    print("===========================================================================================================")
    print("Here assume 'raising' is multiplication on latitude and 'just twice' is addition:")
    print(f"({float(long)+2},{float(lat)*63})")

def option_3(lat, long):
    print("===========================================================================================================")
    print("Here assume 'raising' is addition on latitude and 'just twice' is multiplication:")
    print(f"({float(long)*2},{float(lat)+63})")

def option_4(lat, long):
    print("===========================================================================================================")
    print("Here assume 'raising' is multiplication on latitude and 'just twice' is multiplication:")
    print(f"({float(long)*2},{float(lat)*63})")

def option_5(lat, long):
    print("===========================================================================================================")
    print("Here assume 'raising' is addition on latitude and 'just twice' is squaring:")
    print(f"({float(long)*float(long)},{float(lat)+63})")

def option_6(lat, long):
    print("===========================================================================================================")
    print("Here assume 'raising' is multiplication on latitude and 'just twice' is squaring:")
    print(f"({float(long)*float(long)},{float(lat)*63})")



def option_1y(lat, long, y):
    print("===========================================================================================================")
    print("Here assume 'raising' is addition on latitude and 'just twice' is addition:")
    print(f"({float(long)+2},{y},{float(lat)+63})")

def option_2y(lat, long, y):
    print("===========================================================================================================")
    print("Here assume 'raising' is multiplication on latitude and 'just twice' is addition:")
    print(f"({float(long)+2},{y},{float(lat)*63})")

def option_3y(lat, long, y):
    print("===========================================================================================================")
    print("Here assume 'raising' is addition on latitude and 'just twice' is multiplication:")
    print(f"({float(long)*2},{y},{float(lat)+63})")

def option_4y(lat, long, y):
    print("===========================================================================================================")
    print("Here assume 'raising' is multiplication on latitude and 'just twice' is multiplication:")
    print(f"({float(long)*2},{y},{float(lat)*63})")

def option_5y(lat, long, y):
    print("===========================================================================================================")
    print("Here assume 'raising' is addition on latitude and 'just twice' is squaring:")
    print(f"({float(long)*float(long)},{y},{float(lat)+63})")

def option_6y(lat, long, y):
    print("===========================================================================================================")
    print("Here assume 'raising' is multiplication on latitude and 'just twice' is squaring:")
    print(f"({float(long)*float(long)},{y},{float(lat)*63})")


#===============================================#
#                    "Main"                     #
#===============================================#
if args.latitude != None and args.longitude != None:
    if args.y_value_in != None:
        y = y_earth(args.y_value_in)
        #option_1y(args.latitude, args.longitude, y)
        #option_2y(args.latitude, args.longitude, y)
        #option_3y(args.latitude, args.longitude, y)
        #option_4y(args.latitude, args.longitude, y)
        option_5y(args.latitude, args.longitude, y)
        #option_6y(args.latitude, args.longitude, y)
    else:
        #option_1(args.latitude, args.longitude)
        #option_2(args.latitude, args.longitude)
        #option_3(args.latitude, args.longitude)
        #option_4(args.latitude, args.longitude)
        option_5(args.latitude, args.longitude)
        #option_6(args.latitude, args.longitude)

print("===========================================================================================================")
print("But it was me... Diomede!")
