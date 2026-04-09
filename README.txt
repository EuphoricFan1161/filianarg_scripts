Moshi moshi!

I put together a small python script "cmdline_coord_to_words.py" that:
    1) Takes in a set of coordinates of arbitrary length, these are intended to be Minecraft coordinates
    2) Converts each input coordinate in base 10 to binary
    3) Partitions each binary string into all possible combinations of its bits where none are left unused
    4) Checks to see if these bit combinations match a morse code sequence for letters
    5) Confirms all partition subsets match to a letter and then combines to a string if so
    6) Checks the string agains the nltk 'popular' 'words' set and a small suplemental set I define
    7) Prints out all possible words for each coordinate

I put together another small script "cmdline_words_to_coords.py" to quickly make MC coordinates from words:
    1) Takes in a set of words of arbitrary length
    2) Converts each word to a binary using the morse code sequence
    3) Converts from the binary to base10 integer coordinates
    
I put together one more small script "cmdline_convert_lat_long_to_MC.py" to quickly make conversions from lat,long to MC:
    1) Takes in lat and long
    2) Uses 4 different (and in my opinion simplest) readings of the 0kind riddle to convert to possible MC coords

I need to add a section to describe the new cross product script... WIP

Notes:
    1) MAKE SURE TO ENCLOSE YOUR COORDINATES WITH DOUBLE QUOTES AND PARENTHESES, HAVE NO SPACES, AND USE THE
       -c COMMAND LINE ARGUMENT!!!  Example of usage for x, y, and z coordinates: 
       python3 ./cmdline_coord_to_words.py -c "(1617,30,439)"
    2) Note, by default the bit to morse convention is 0 := '-' and 1 := '.', this can be swapped using the cmd 
       line args.  The convention and method is chosen due to the original choice by Fog_runner on the 
       "Coords calculation" page of the ARG document.  Fog_runner found when using the coordinates "(1617,30,439)", 
       they could make the words "SET" from 30 and "FREE" from 439 using the same method detailed about (I am not 
       sure if they were doing this by hand or code).  Using my implementation and the nltk dataset, I was able to 
       find the word "UNTAME" from 1617, resulting in the coordinates "(1617,30,439)" ==> "(UNTAME,SET,FREE)".  
       Due to this initial success, I stuck to this convention.  There are however other possiblilites for the 
       y and z coordinates.  I encourage you to use "(1617,30,439)" as the first set of coordinates you try.
    3) Verbosity can be changed by the cmd line arguments giving a detailed readout at certain stages of the
       processing
    4) To run the "cmdline_coord_to_words.py" script you will need to install nltk (Natural Language Toolkit) if you 
       do not already have it installed.  I used python version 3.13.12.  The instructions to install nltk can be found 
       here https://www.nltk.org/install.html or with a quick google of "python nltk install".  You must download the
       dataset you wish to use after installing the nltk package, the instructions can be found at the same link.
       I used the 'popular' download and the 'words' set in the script, feel free to try others, maybe there is 
       something else there?
    5) The "cmdline_words_to_coords.py" script contains a degeneracy in it's solutions as we assume an absolute value
       has been taken on the integer outputs like we did for the "cmdline_coord_to_words.py" script inputs.  To be sure,
       all sets of possible negated coordinates should be checked.  A good test example to try is "(UNTAME,SET,FREE)" as
       we know what coordinates can generate this text from the other script.
    
Enjoy! :3

Writen by TH3EEuphoricFan1161

Do whatever you want with the code, play around with it and make it better


But it was me... Diomede!