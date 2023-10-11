import os
import json
import sys

errors_sub = ["Term_Resource", "Term_Inconsistent", "Term_Wrong", "Acc_Mistrans", "Acc_Overtrans", "Acc_Undertrans",
          "Acc_Add", "Acc_Omi", "Acc_DNT", "Acc_Untrans", "Ling_Grammar",
          "Ling_Punct", "Ling_Spelling", "Ling_Unintelligible", "Ling_Encoding", "Style_Org", "Style_Third",
          "Style_Register", "Style_Awkward", "Style_Unidimoatic", "Style_Inconsistent", "Loc_Number",
          "Loc_Currency", "Loc_Measure", "Loc_Time", "Loc_Date", "Loc_Addr", "Loc_Tel", "Loc_Shortc",
          "AudienceAppropriateness", "DesignMarkup"]

errors_main = ["Terminology", "Accuracy", "Linguistic Conventions", "Style", "Locale", "Audience Appropriateness", "Design and Markup"]


def write_error_dict(error_dict, outfile):
    with open(outfile, "w", encoding="utf-8") as fo:
        for key, value in error_dict.items():
            new_list = [key] + [str(item) for item in value]
            fo.write("\t".join(new_list)+"\n")

def make_error_dict(errors_list):
    error_dict = {}

    for e in errors_list:
        # severity values: normal, minor, major, critical
        error_dict[e] = [0, 0, 0, 0]

    return error_dict

def calculate_sents_with_errors(sents_with_errors_dict, error_dict_file):
    opennmt_sents = []
    modernmt_sents = []
    deepl_sents = []
    for key, value in error_dict_file.items():
        if key == "SRC":continue
        for v in value:
            if v[-1].startswith("sent"):
                sent_id = int(v[-1].replace("sent", ""))
                if key == "deepl": deepl_sents.append(sent_id)
                elif key == "opennmt": opennmt_sents.append(sent_id)
                elif key == "modernmt": modernmt_sents.append(sent_id)
                else: continue

    opennmt_sents = list(set(opennmt_sents))
    modernmt_sents = list(set(modernmt_sents))
    deepl_sents = list(set(deepl_sents))
    sents_with_errors_dict["deepl"] += len(deepl_sents)
    sents_with_errors_dict["opennmt"] += len(opennmt_sents)
    sents_with_errors_dict["modernmt"] += len(modernmt_sents)

def calculate_mqm(deepl_dict, opennmt_dict, modernmt_dict, src_dict, error_dict_file):
    for key, value in error_dict_file.items():
        print()
        print(key)

        for e in errors_sub:
            for v in value:
                if v[0] == e:
                    try:
                        severity = int(v[1])
                        # Increment error for each specific severity type
                        if key == "deepl": deepl_dict[e][severity]+=1
                        elif key == "opennmt": opennmt_dict[e][severity]+=1
                        elif key == "modernmt": modernmt_dict[e][severity]+=1
                        elif key == "SRC": src_dict[e][severity]+=1
                    except:
                        if key == "SRC":
                            # for SRC segments only increment neutral severity type
                            src_dict[e][0] += 1
                        else:
                            print("No severity found for:")
                            print(key, value)
                            sys.exit()



def analyse(folder_input):

    deepl_dict = make_error_dict(errors_sub)
    opennmt_dict = make_error_dict(errors_sub)
    modernmt_dict = make_error_dict(errors_sub)
    src_dict = make_error_dict(errors_sub)

    # Create a dictionary to count sentences with errors per system
    sents_with_errors_dict = {"deepl":0, "opennmt":0, "modernmt": 0}

    # Loop over each file in the folder
    for filename in os.listdir(folder_input):
        # Check if the file is a JSON file
        if filename.endswith(".json"):
            print()
            print(filename)
            print("___________________________")
            # Open the file and read its contents
            with open(os.path.join(folder_input, filename), "r") as file:
                error_dict_file = json.load(file)
                print(error_dict_file)
                calculate_mqm(deepl_dict, opennmt_dict, modernmt_dict, src_dict, error_dict_file)
                calculate_sents_with_errors(sents_with_errors_dict, error_dict_file)

    out_opennmt = os.path.join(folder_input, "opennmt_mqm.txt")
    out_deepl = os.path.join(folder_input, "deepl_mqm.txt")
    out_modernmt = os.path.join(folder_input, "modernmt_mqm.txt")
    print("OpenNMT:")
    print(opennmt_dict)
    write_error_dict(opennmt_dict, out_opennmt)
    print("")
    print("DeepL:")
    print(deepl_dict)
    write_error_dict(deepl_dict, out_deepl)
    print("")
    print("ModernMT:")
    print(modernmt_dict)
    write_error_dict(modernmt_dict, out_modernmt)
    print("")
    print("SRC:")
    print(src_dict)
    print("")
    print("Sentences with errors:")
    print(sents_with_errors_dict)



if __name__ == '__main__':
    # Check if the folder path and the term list are provided as a command-line argument
    if len(sys.argv) != 2:
        print('Usage: python labelstudio_analyse_annotations.py <folder_input>')
        sys.exit(1)


    folder_input = sys.argv[1]

    # Call the analyse function
    analyse(folder_input)
