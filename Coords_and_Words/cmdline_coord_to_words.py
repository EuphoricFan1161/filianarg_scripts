#Writen by TH3EEuphoricFan1161
import argparse
import nltk # type: ignore
from nltk.corpus import words # type: ignore


#================================================#
#                    Argparse                    #
#================================================#
parser = argparse.ArgumentParser()
parser.add_argument("-dpt", "--do_partitioning_test", action="store_true", help="Run the partitioning test to display example of arbitrary string partitioning")
parser.add_argument("-vt", "--verbose_text", action="store_true", help="Also returns the strings that this code did not find to be words")
parser.add_argument("-vp", "--verbose_partitioning", action="store_true", help="Prints the entire set of binary partitions (can get large for large integer coordinates)")
parser.add_argument("-c", "--coordinates", type=str, default=None, help='Enter MC coordinates as "(x,y,z)" with the ""s and no spaces!  You may enter N_dimensions \u2208 [1, inf)')
parser.add_argument("-fc", "--flip_convention", action="store_true", help="Flip morse convention of 0 := '-' and 1 := '.' to 0 := '.' and 1 := '-'")
parser.add_argument("-n", "--keep_negative", action="store_true", help="Instead of dropping negatives completely, assume they are a leading dash")
parser.add_argument("-f", "--file", action="store_true", help='Use a file instead (not implemented yet)')
args = parser.parse_args()


#===============================================#
#              Define Dictionaries              #
#===============================================#
#Let us use the convention of 0 := "-" and 1 := "." for the sake of checking our work on "UNTAME/SET/FREE"
#I will directly implement this into the dictionary, allowing for bin --> words directly using morse code patterning
MORSE_TO_LETTER = {'10':'A', '0111':'B',
                    '0101':'C', '011':'D', '1':'E',
                    '1101':'F', '001':'G', '1111':'H',
                    '11':'I', '1000':'J', '010':'K',
                    '1011':'L', '00':'M', '01':'N',
                    '000':'O', '1001':'P', '0010':'Q',
                    '101':'R', '111':'S', '0':'T',
                    '110':'U', '1110':'V', '100':'W',
                    '0110':'X', '0100':'Y', '0011':'Z'}


#================================================#
#   Define Functions for Coordinates --> Words   #
#================================================#
def is_english_word(word, english_vocab):
    is_in_nltk = word.lower() in english_vocab
    is_in_suplemental = word.lower() in ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "sept", "oct", "nov", "dec", "mon", "tues", "wed", "thurs", "fri", "est", "diomede", "im"]
    return is_in_nltk or is_in_suplemental

def generate_binary_from_base10(coord):
    ret_bin = bin(abs(coord))[2:]
    if args.flip_convention:
        transposition_table = str.maketrans("01", "10")
        ret_bin = ret_bin.translate(transposition_table)
    #implement inclusion of leading minuses here
    if args.keep_negative and (coord < 0):
        if args.flip_convention:
            ret_bin = "1" + ret_bin
        else:
            ret_bin = "0" + ret_bin
    return ret_bin

def partition(binary):
    if not binary:
        return [[]]
    result = []
    for i in range(1, len(binary) + 1):
        prefix = binary[:i]
        for rest in partition(binary[i:]):
            result.append([prefix] + rest)
    return result

def create_potential_word_list(this_coord_partition, english_vocab):
    found_words = []
    remaining_letter_combos = []
    for potential_word in this_coord_partition:
        this_letter_combo = ""
        for potential_letter in potential_word:
            this_letter_combo += MORSE_TO_LETTER.get(potential_letter,"*")
        if "*" in this_letter_combo:
            #throw out any word where a letter does not exist in the morse dictionary
            continue
        #Now check to see if it is a known english word
        if is_english_word(this_letter_combo, english_vocab):
            found_words.append(this_letter_combo)
        else: 
            remaining_letter_combos.append(this_letter_combo)
    return [found_words, remaining_letter_combos]

def do_MC_input(coordinate_str, english_vocab):
    coordinate_vector = coordinate_str[1:-1].split(",")
    print(f"You entered coordinates {coordinate_vector}")
    if args.flip_convention:
        print("Converting to binary using absolute values and FLIPPED CONVENTION...")
    else:
        print("Converting to binary using absolute values...")
    binary_coordinate_vector = [] #If brute forcing a bin, just place here and comment the below two lines ('01010010001000010001001010')
    for coordinate in coordinate_vector:
        binary_coordinate_vector.append(generate_binary_from_base10(int(coordinate)))
    print(f" --> {binary_coordinate_vector}")
    print("Partitioning binary sequences...")
    partition_vector = []
    for bin_coord in binary_coordinate_vector:
        partition_vector.append(partition(bin_coord))
        if args.verbose_partitioning:
            print(f"{bin_coord} --> {partition_vector[-1]}")
    print("Searching for possible morse code letter combinations...")
    possible_english_words = []
    remaining_letter_combos = []
    for this_coord_partition in partition_vector:
        english_result = create_potential_word_list(this_coord_partition, english_vocab)
        possible_english_words.append(english_result[0])
        remaining_letter_combos.append(english_result[1])
    print("===========================================================================================================")
    print("Potential strings matched to words in the ntlk english 'popular' 'words' set or my suplemental list")
    for i in range(len(possible_english_words)):
        print(f"{coordinate_vector[i]} --> {possible_english_words[i]}")
    print("===========================================================================================================")
    if args.verbose_text:
        print("Strings that were not matched to words in the ntlk english 'popular' 'words' dataset or my suplemental list")
        for i in range(len(remaining_letter_combos)):
            print(f"{coordinate_vector[i]} --> {remaining_letter_combos[i]}")
        print("===========================================================================================================")


#===============================================#
#                    "Main"                     #
#===============================================#
print_reminder = bool(not args.do_partitioning_test and (args.coordinates == None) and not args.file)
if print_reminder:
    print(" === PLEASE BE SURE TO READ THE ARG PARSER === ")
    quit()

english_vocab = set(w.lower() for w in words.words())

if args.do_partitioning_test:
    print("Example partition of the string '1234':")
    result = partition("1234")
    print(result)
    print("In practice this is be carried out on binary sequences to break them into potential morse code letter combinations")

if args.coordinates != None:
    #Base behaviour
    do_MC_input(args.coordinates, english_vocab)

    #specific testing
    #test_str = "(0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44)"
    #do_MC_input(test_str, english_vocab)

print("But it was me... Diomede!")
