#Writen by TH3EEuphoricFan1161
import argparse


#================================================#
#                    Argparse                    #
#================================================#
parser = argparse.ArgumentParser()
parser.add_argument("-w", "--word_vec", type=str, default=None, help='Enter words as "(abc,def,ghi)" with the ""s and no spaces!  You may enter N_dimensions \u2208 [1, inf)')
parser.add_argument("-fc", "--flip_convention", action="store_true", help="Flip morse convention of 0 := '-' and 1 := '.' to 0 := '.' and 1 := '-'")
args = parser.parse_args()


#===============================================#
#              Define Dictionaries              #
#===============================================#
#Let us use the convention of 0 := "-" and 1 := "." for the sake of checking our work on "UNTAME/SET/FREE"
#I will directly implement this into the dictionary, allowing for words --> bin directly using morse code patterning
LETTER_TO_MORSE = { 'A':'10', 'B':'0111',
                    'C':'0101', 'D':'011', 'E':'1',
                    'F':'1101', 'G':'001', 'H':'1111',
                    'I':'11', 'J':'1000', 'K':'010',
                    'L':'1011', 'M':'00', 'N':'01',
                    'O':'000', 'P':'1001', 'Q':'0010',
                    'R':'101', 'S':'111', 'T':'0',
                    'U':'110', 'V':'1110', 'W':'100',
                    'X':'0110', 'Y':'0100', 'Z':'0011'}


#================================================#
#   Define Functions for Words --> Coordinates   #
#================================================#
def convert_word_to_bin_through_morse(word):
    binary = ""
    for letter in word:
        binary += LETTER_TO_MORSE.get(letter.upper(),"*")
    if "*" in binary:
        print("Failed to find a matching letter in the morse dictionary!")
        quit()
    return binary

def convert_to_coords(word_str):
    word_vector = word_str[1:-1].split(",")
    binary_coordinates = []
    for word in word_vector:
        ret_bin = convert_word_to_bin_through_morse(word)
        if args.flip_convention:
            transposition_table = str.maketrans("01", "10")
            ret_bin = ret_bin.translate(transposition_table)
        binary_coordinates.append(ret_bin)
    degenerate_base10_coordinates = []
    for coord in binary_coordinates:
        degenerate_base10_coordinates.append(int(coord, 2))
    print("===========================================================================================================")
    print("MC coordinates from text, note degeneracy the sign of solutions!  Check all sign combinations!")
    for i in range(len(word_vector)):
        print(f"{word_vector[i]} --> {degenerate_base10_coordinates[i]} from binary/morse {binary_coordinates[i]}")
    print("===========================================================================================================")


#===============================================#
#                    "Main"                     #
#===============================================#
if args.word_vec != None:
    convert_to_coords(args.word_vec)

print("But it was me... Diomede!")
