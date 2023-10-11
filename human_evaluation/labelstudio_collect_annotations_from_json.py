import json
import sys
import os


def get_mt_offsets(folder_input, input_file_name):
    """
    Collect start-end character offsets for each MT output
    :param items: folder_input, input_file_name
    :return: A dictionary of lists of offsets
    """
    with open(os.path.join(folder_input, input_file_name), "r", encoding="utf-8") as fi:
        mt_offsets = {"SRC": [], "MT1": [], "MT2":[], "MT3":[] }

        offset = 0
        for line in fi:
            if line.startswith("SRC"):
                start_offset = offset
                end_offset = offset + len(line)
                mt_offsets["SRC"].append((start_offset, end_offset))
            else:
                for j in range(1,4):
                    if line.startswith('MT'+str(j)):
                        start_offset = offset
                        end_offset = offset + len(line)
                        mt_offsets["MT"+str(j)].append((start_offset, end_offset))
                    else:
                        continue
            offset += len(line)
    return mt_offsets

def get_sent_offsets(foler_input, input_file_name):
    with open(os.path.join(folder_input, input_file_name), "r", encoding="utf-8") as fi:
        sent_offsets = {}

        offset = 0
        seg_count = 0
        for line in fi:
            if line.startswith("SRC"):
                start_offset = offset
            elif line.startswith("MT3:"):
                end_offset = offset + len(line)
                seg_count += 1
                sent_offsets[seg_count] = (start_offset, end_offset)
            else: pass
            offset += len(line)
    return sent_offsets

def get_mt_id(start_id, mt_offsets):
    #print(start_id)
    for key, value in mt_offsets.items():
        #print(key, value)
        for v in value:
            #print(v)
            if start_id >= v[0] and start_id < v[1]:
                return(key)

    return("SRC")

def get_sent_id(start_id, sent_offsets):
    #print(start_id)
    for key, value in sent_offsets.items():
        #print(key, value)
        if start_id >= value[0] and start_id < value[1]:
            #print(key)
            return(key)
        else: continue
    sys.exit("No sent found.")
    #return(None)

def normalize_error_dict(error_dict, file_mt_log, input_file_name):
    """
    Normalize the format of the error annotations dictionary to MTX : [label, severity, start-end-offsets]
    :param error_dict: error_dict
    :return: normalized dictionary
    """

    mt_log_lines =  open(file_mt_log, "r", encoding="utf-8").readlines()
    file_base = os.path.splitext(input_file_name)[0]
    for line in mt_log_lines:
        print(line)
        if line.startswith(file_base):
            mt_systems = line.strip().split("\t")


    new_dict = dict()
    for key, value in error_dict.items():
        key_items = key.split("_")

        if key_items[0].startswith("MT"):
            for i in range(1,4):
                if key_items[0] == "MT"+str(i):
                    value.append(key_items[0])
                    value.append(key_items[1])
                    value.append(key_items[2])

                    # retrieve the MT system from the list mt_systems
                    new_key = mt_systems[i]
                    break
        elif key_items[0] == "SRC":
            value.append(key_items[0])
            value.append(key_items[1])
            value.append(key_items[2])
            new_key = "SRC"

        if not new_key in new_dict:
            new_dict[new_key] = [value]
        else:
            new_dict[new_key].append(value)



    return(new_dict)

def get_error_annotations(folder_input, input_file_name, mt_offsets, sent_offsets, item):
    """
        Collect error annotations for the input_file_name MTX : [label, severity, start-end-offsets]
        :param error_dict: error_dict
        :return: normalized dictionary
        """
    error_dict = dict()
    with open(os.path.join(folder_input, input_file_name), "r", encoding='utf-8') as fi:
        fi_content = fi.read()
        print(fi_content)

        for label in item["label"]:
            start_id = int(label["start"])
            end_id = int(label["end"])
            print("START-END")
            print(start_id)
            print(end_id)
            mt_id = get_mt_id(start_id, mt_offsets)
            print(label["text"])
            text_match = fi_content[start_id:end_id]
            print(text_match)
            print(mt_id)
            print(label["labels"])

            sent_id = get_sent_id(start_id, sent_offsets)
            print(sent_id)
            if not mt_id + "_" + str(start_id)+"-"+str(end_id) + "_sent" + str(sent_id) in error_dict:
                error_dict[mt_id + "_" + str(start_id)+"-"+str(end_id) + "_sent" + str(sent_id)] = label["labels"]
            else:
                error_dict[mt_id + "_" + str(start_id) + "-" +
                str(end_id) + "_sent" + str(sent_id)] += label["labels"]
            print("")

    # Sort the list of labels so that error label + severity always appears in the same order
    for key, value in error_dict.items():
        error_dict[key] = sorted(value, reverse=True)
    return(error_dict)




def analyse(json_output, folder_input, file_mt_log):
    # Get the list of JSON files in the folder

    input_files = [f for f in os.listdir(folder_input) if f.endswith('.merged')]
    print(input_files)



    # Write the names of the JSON files to the output file

    with open(json_output, 'r') as json_file:
        json_data = json.load(json_file)
        out_dir = os.path.dirname(os.path.abspath(json_output))

        for item in json_data:
            input_file_name = item["text"].split("-")[-1]
            print(input_file_name)
            if input_file_name in input_files:

                mt_offsets = get_mt_offsets(folder_input, input_file_name)
                print(mt_offsets)

                sent_offsets = get_sent_offsets(folder_input, input_file_name)
                print(sent_offsets)

                error_dict = get_error_annotations(folder_input, input_file_name, mt_offsets, sent_offsets, item)
                print(error_dict)

                normalized_error_dict = normalize_error_dict(error_dict, file_mt_log, input_file_name)
                print(normalized_error_dict)


                # Open the output file for writing
                with open(os.path.join(out_dir, input_file_name+".annotations.json"), 'w') as f:
                    # use the json.dump() method to write the dictionary in pretty printed format
                    json.dump(normalized_error_dict, f, indent=2)


            else:
                continue




if __name__ == '__main__':
    # Check if the folder path and the term list are provided as a command-line argument
    if len(sys.argv) != 4:
        print('Usage: python labelstudio_collect_annotations_from_json.py <json_output> <folder_input> <file_mt_log>')
        sys.exit(1)


    json_output = sys.argv[1]
    folder_input = sys.argv[2]
    file_mt_log = sys.argv[3]

    # Call the analyse function
    analyse(json_output, folder_input, file_mt_log)
