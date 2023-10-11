import os
import sys
import pandas as pd
import spacy
from spacy.tokenizer import Tokenizer
from spacy.tokens import Doc


# Tested using Spacy version: 3.5.2
# Requires the English transformer model of Spacy: en_core_web_trf

def compare_filenames(file1, file2):
    """
    Compares the names of two files without the file extension.
    :param file1: The first file.
    :param file2: The second file.
    :return: True if the names match, False otherwise.
    """
    # Get the base names (names without the path) of the files
    file1_base_name = os.path.splitext(os.path.basename(file1))[0]
    file2_base_name = os.path.splitext(os.path.basename(file2))[0]

    # Compare the base names without case sensitivity
    if file1_base_name.lower() == file2_base_name.lower():
        return True
    else:
        return False



def collect_src_terms_to_lists(file_path, lang):
    """
    Reads a TSV file and collects the source terms (first item)
    :param file_path: The path of the TSV file to read.
    :return: A list containing the source terms
    """
    # Initialize empty lists to store the first and second items
    src_items = []

    # Open the TSV file in read mode
    with open(file_path, 'r') as file:
        # Loop through each line in the file
        for line in file:
            # Strip leading and trailing whitespaces and split the line by tabs
            items = line.strip().split('\t')
            # Check if the line has at least two items
            if len(items) >= 2:
                if items[0] == "src_term" and items[1] == "trg_term":
                    continue
                # Append the first item to the first_items list
                # items[0] is the English term
                # src_items.append(items[0])
                if lang == "fr":
                    # items[1] is the French term
                    src_items.append(items[1])
                elif lang == "en":
                    # Otherwise add the English term
                    src_items.append(items[0])



    return src_items


def lemmatize_items(items, nlp):
    """
    Lemmatizes the items in a list using Spacy.
    :param items: The list of items to lemmatize.
    :return: A list of lemmatized items.
    """
    # Load the Spacy English language model
    # Initialize an empty list to store the lemmatized items
    lemmatized_items = []
    # Loop through each item in the input list
    for item in items:
        # Process the item with Spacy
        doc = nlp(item)
        # Get the lemmatized form of the item and append it to the lemmatized_items list
        # lemmatized_item = ' '.join([token.lemma_ for token in doc]).replace(" ™", "™")
        lemmatized_item = []
        for token in doc:
            if token.text.isupper():
                lemmatized_item.append(token.text)
            else:
                lemmatized_item.append(token.lemma_)
        lemmatized_items.append(lemmatized_item)
    # Return the list of lemmatized items
    return lemmatized_items



def mark_terms(src_line, lem_term_list, nlp, term_count, file_with_term_count):
    # Process the sentence with spaCy
    doc = nlp(src_line)

    # matched terms
    matched_terms = []

    # Create a list of token ids that match with all terms
    list_token_ids = []

    for term in lem_term_list:

        # Loop through each token in the processed sentence
        for i in range(len(doc) - len(term) + 1):
            # Check if the current sequence of token lemmas match the tokens to search for
            # Terms are only lemmatized if fully lowercase (i.e. LUHMES cells > LUHMES cell)
            # This is taken account when matching text
            # > terms with uppercase chars should match the casing
            # > terms that are lowercased/lemmatized can match any casing combination
            if all(doc[i + j].lemma_ == term[j] or doc[i + j].lower_ == term[j] or doc[i + j].text == term[j] for j in range(len(term))):
                # Create a list to store the token IDs for a specific term
                token_ids = []
                # Add the tokens' IDs to the list
                for j in range(len(term)):
                    token_ids.append(doc[i + j].i)

                # Also store the matched term to check later
                matched_terms.append(term)

                list_token_ids.append(token_ids)

    # Filter out empty token_id lists
    list_token_ids = list(filter(None, list_token_ids))
    if len(list_token_ids) > 0:
        term_count += len(list_token_ids)
        file_with_term_count += 1


    # Wrap all the corresponding words in doc with << >> and add them to a new_token list
    # Preserve the spacy whitespaces to detokenize afterwards correctly
    new_tokens = []
    for token in doc:
        if starting_term(token, list_token_ids) and not ending_term(token, list_token_ids):
            new_tokens.append("<<" + token.text + token.whitespace_)
        elif starting_term(token, list_token_ids) and ending_term(token, list_token_ids):
            new_tokens.append("<<" + token.text + ">>" + token.whitespace_)
        elif not starting_term(token, list_token_ids) and ending_term(token, list_token_ids):
            new_tokens.append(token.text + ">>" + token.whitespace_)
        else:
            new_tokens.append(token.text_with_ws)


    # Create a new doc object to be able to detokenize using trailing whitespaces
    new_doc = Doc(doc.vocab, words=new_tokens)
    new_src_line = ''.join([token.text for token in new_doc])

    # Print the sentence if any terms have been marked
    if new_src_line != src_line:
        print(matched_terms)
        print(list_token_ids)
        print(new_src_line.strip())
        print("")

    # return the sentence marked with terms
    return(new_src_line, term_count, file_with_term_count)


def starting_term(token, list_token_ids):
    starting = False
    for item in list_token_ids:
        if token.i == item[0]:
            return True
    return starting

def ending_term(token, list_token_ids):
    ending = False
    for item in list_token_ids:
        if token.i == item[-1]:
            return True
    return ending

def preprocess(folder_path, term_file, lang):
    """
    Preprocess data.
    Reads src(en) - target(fr) text pairs and the termlist
    Produces an output file with src/mt/blankline per segment.
    Terms in the src sentences are additionally marked with <<term>>

    Args:
        folder_path (str): Path of the folder containing the .en and .fr file pairs
        termlist: .tsv file containing the termlist from the given domain
    """



    if lang == "fr":
        # Load the Spacy French language model - transformer based
        nlp = spacy.load('fr_dep_news_trf', disable=['parser', 'ner'])
    elif lang == "en":
        # Load the spaCy English language model (transformer-based) and disable unnecessary processing
        nlp = spacy.load('en_core_web_trf', disable=['parser', 'ner'])
    else:
        sys.exit("Language not implemented. Please choose en or fr.")

    print("SpaCy version:" + str(spacy.__version__))

    # Collect src terms
    src_terms = collect_src_terms_to_lists(term_file, lang)

    # Lemmatize terms (unless contains an uppercase character)
    print("Lemmatizing terms ... ")
    src_lem_terms = lemmatize_items(src_terms, nlp)


    # print lemmatized terms
    for item in src_lem_terms:
        print(item)
    print("")


    # Get all .en and .fr files in the folder (sorted)
    src_files = sorted([f for f in os.listdir(folder_path) if f.endswith('.en')])
    tgt_files = sorted([f for f in os.listdir(folder_path) if f.endswith('.fr')])


    # count total no of terms and files with terms
    term_count = 0
    file_with_term_count = 0
    file_count = 0

    # Iterate through each file
    for sf, tf in zip(src_files, tgt_files):
        file_count += 1
        if compare_filenames(sf, tf):

            src_file = os.path.join(folder_path, sf)
            tgt_file = os.path.join(folder_path, tf)

            # Create output file name
            merged_file = os.path.join(folder_path, os.path.splitext(os.path.basename(sf))[0] + ".merged")


            # Read input files and create the output file (merged)
            with open(src_file, 'r') as src, open(tgt_file, 'r') as tgt, open(merged_file, 'w') as merged_f:
                src_lines = src.readlines()
                tgt_lines = tgt.readlines()
                if len(src_lines) != len(tgt_lines):
                    print(src_file, tgt_file, "line numbers don't match")
                    sys.exit()

                for s, t in zip(src_lines, tgt_lines):
                    # Mark terms in the source line
                    marked_s, term_count, file_with_term_count = mark_terms(s, src_lem_terms, nlp, term_count, file_with_term_count)

                    # Write to output file
                    merged_f.write(marked_s)
                    merged_f.write(t)
                    merged_f.write("\n")


                print('Output file created:', merged_file)

        else:
            print("Mismatching file names")
            print(sf)
            print(tf)
            sys.exit()
    print("Total no. of files: "+str(file_count))
    print("Total no. of terms: "+str(term_count))
    print("Total no. of files with at least one term: "+str(file_with_term_count))

if __name__ == '__main__':
    # Check if the folder path and the term list are provided as a command-line argument
    if len(sys.argv) != 4:
        print('Usage: python labelstudio_prepare_input.py <folder_path_to_src-ref> <path_to_termlist> <language>')
        sys.exit(1)

    # Get the folder path from command-line argument
    folder_path = sys.argv[1]
    term_file = sys.argv[2]
    lang = sys.argv[3]

    # Call the function to read Excel files in the folder
    preprocess(folder_path, term_file, lang)
