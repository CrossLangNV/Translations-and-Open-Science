import os
import sys
import pandas as pd
import json

def get_text_info(excel_file, set_id):
    # read the Excel file into a DataFrame
    df = pd.read_excel(excel_file)
    text_info_list = []

    # loop over the rows in the DataFrame
    for index, row in df.iterrows():
        if not pd.isna(df.loc[index, 'origin']) and not pd.isna(df.loc[index, 'type']) \
                and not pd.isna(df.loc[index, 'file_name'] and not pd.isna(df.loc[index, 'text'])):
            #print(df.loc[index, 'origin'])
            # Add a tuple of (MT system, file_type, file_name)
            no_words_text = len(df.loc[index, 'text'].split())
            no_words_sent_list = [len(item.split()) for item in df.loc[index, 'text'].split("\\n")]
            # Add 1 to the end of list for the segment "end_of_text", which is not counted so far
            no_words_sent_list.append(1)

            text_info_list.append((df.loc[index, 'origin'], df.loc[index, 'type'], df.loc[index, 'file_name'], set_id, no_words_text, no_words_sent_list))
    return text_info_list

def add_item(mt_dict, line_tokens, i, text_info_list, tgt_lang):

    # Participant id is stored as the 4th item in the list
    participant = line_tokens[3]
    # The item after the question is the answer (0 or 1)
    if tgt_lang.lower() == "en":
        quest_index = line_tokens.index("Is the following statement cor")
    elif tgt_lang.lower() == "fr":
        print(line_tokens)
        quest_index = line_tokens.index("L'affirmation suivante est-ell")
    quest_answer = line_tokens[quest_index + 1]
    if quest_answer == "1":
        quest_answer = "correct"
    else:
        quest_answer = "wrong"
    # The first occurence of -9999 marks the end of timing
    if "-9999" in line_tokens:
        end_timing_index = line_tokens.index("-9999")
    timing_list = line_tokens[quest_index + 2:end_timing_index]
    file_type = text_info_list[i - 1][1]
    file_name = text_info_list[i - 1][2]
    set_id = text_info_list[i - 1][3]
    no_words_text = text_info_list[i - 1][4]
    no_words_sent_list = text_info_list[i - 1][5]


    results = [participant, quest_answer, timing_list, file_type, file_name, set_id, no_words_text, no_words_sent_list]
    if str(i) in mt_dict:
        mt_dict[str(i)].append(results)
    else:
        mt_dict[str(i)] = [results]

def add_quality(mt_dict, line_tokens, i, tgt_lang):
    if tgt_lang.lower() == "en":
        lang_quest = "Was the translation of suffici"
    elif tgt_lang.lower() == "fr":
        lang_quest = "La qualité de la traduction ét"

    if lang_quest in line_tokens:
        quality_answer = line_tokens[line_tokens.index(lang_quest) + 1]
        """
        if tgt_lang.lower() == "en":
            quality_answer = line_tokens[line_tokens.index("Was the translation of suffici") + 1]
        elif tgt_lang.lower() == "fr":
            quality_answer = line_tokens[line_tokens.index("La qualité de la traduction ét") + 1]
        """
        if quality_answer == "1": quality_answer = "True"
        else: quality_answer = "False"
        if str(i) in mt_dict:
            # Add the answer on quality to the other info obtain from the same participant on the same text
            # This should be always the last item in the list of values
            mt_dict[str(i)][-1].append(quality_answer)
    else:
        print(line_tokens)
        sys.exit("Incorrect line found for quality assessment.")

def write_to_csv(mt_dict, outfile_sent, outfile_text, domain, tgt_lang, mt_system):
     for i in range(0, len(mt_dict.keys())):
        text_id = str(i + 1)
        print("")
        print(mt_dict[text_id])
        # For each text id results from all participants are stored as a list
        # Loop over the results per participant
        for item in mt_dict[text_id]:
            participant = item[0]
            qanswer = item[1]
            file_type = item[3]
            file_name = item[4]
            set_id = item[5]
            no_words_text = item[6]
            no_words_sent_list = item[7]
            if item[8] == "True": quality = "yes"
            else: quality = "no"
            sents = item[2]
            # Loop over all sentence readings
            for j in range(0, len(sents)):
                sent_id = j + 1
                sent_time = item[2][j]
                no_words_sent = no_words_sent_list[j]
                sent_time_per_word = round(int(sent_time)/no_words_sent, 2)

                # Text id is end_of_text if it is the last sentence in a given text
                if j == len(sents) - 1:
                    text_sent_id = "T" + str(text_id) + "_end"
                else:
                    text_sent_id = "T" + str(text_id) + "-" + "S" + str(sent_id)
                print(domain, tgt_lang, file_type, text_sent_id, set_id, mt_system, participant, sent_time, str(no_words_sent), str(sent_time_per_word))
                outfile_sent.write("\t".join([domain, tgt_lang, file_type, text_sent_id, set_id, mt_system, participant, sent_time, str(no_words_sent), str(sent_time_per_word)])+"\n")

            print(sents)
            int_sents = [int(item) for item in sents]
            tot_read_time_wo_end = str(sum(int_sents[:-1]))
            tot_read_time_with_end = str(sum(int_sents))
            tot_read_time_wo_end_norm = round(int(tot_read_time_wo_end)/no_words_text, 2)
            tot_read_time_with_end_norm = round(int(tot_read_time_with_end)/no_words_text, 2)
            print(domain, tgt_lang, file_type, "T" + str(text_id), set_id, mt_system, participant, tot_read_time_wo_end,
                  tot_read_time_with_end, no_words_text, tot_read_time_wo_end_norm, tot_read_time_with_end_norm, qanswer, quality)
            outfile_text.write("\t".join([domain, tgt_lang, file_type, "T" + str(text_id), set_id, mt_system, participant, tot_read_time_wo_end,
                  tot_read_time_with_end, str(no_words_text), str(tot_read_time_wo_end_norm), str(tot_read_time_with_end_norm), qanswer, quality]) + "\n")


def analyse(folder_input, domain, tgt_lang):
    """
    Reads Zepman export files and the xlsx files in which texts are defined (per MT engine)
    and analyses the reading times

    Args:
        folder_path (str): Path of the folder containing the zeoman export files (CSV)
        set_id (int): Set ID that indicates the experiment set
    """
    # Create empty dictionaries where the info per engine will be stored
    deepl_dict = dict()
    opennmt_dict = dict()
    modernmt_dict = dict()
    humant_dict = dict()

    # Loop over files for each 4 set
    #for id in range(1,5):
    for id in range(1, 2):
        set_id = "set"+str(id)
        # Get text info from the excel file'
        text_info_list = get_text_info(os.path.join(folder_input, set_id + ".xlsx"), set_id)
        print(text_info_list)

        # loop over all files in the folder
        for file_name in os.listdir(folder_input):
            if set_id in file_name and file_name.endswith(".csv"):
                print(file_name)
                # open the file
                with open(os.path.join(folder_path, file_name), "r") as file:
                    # count text fragments to match with MT IDs
                    text_count = 0

                    # read the file contents
                    file_lines = file.readlines()
                    for i in range(0, len(file_lines)):
                        if tgt_lang.lower() == "en":
                            lang_text = "Is the following statement"
                        elif tgt_lang.lower() == "fr":
                            lang_text = "L'affirmation suivante est-ell"

                        if lang_text in file_lines[i]:
                            print("tgt_lang found")
                            text_count += 1
                            line_tokens = file_lines[i].split(";")
                            next_line_tokens = file_lines[i+1].split(";")

                            if text_info_list[text_count - 1][0] == "DeepL":
                                add_item(deepl_dict, line_tokens, text_count, text_info_list, tgt_lang)
                                add_quality(deepl_dict, next_line_tokens, text_count, tgt_lang)
                            elif text_info_list[text_count - 1][0] == "ModernMT":
                                add_item(modernmt_dict, line_tokens, text_count, text_info_list, tgt_lang)
                                add_quality(modernmt_dict, next_line_tokens, text_count, tgt_lang)
                            elif text_info_list[text_count - 1][0] == "OpenNMT":
                                add_item(opennmt_dict, line_tokens, text_count, text_info_list, tgt_lang)
                                add_quality(opennmt_dict, next_line_tokens, text_count, tgt_lang)
                            elif text_info_list[text_count - 1][0] == "HT":
                                add_item(humant_dict, line_tokens, text_count, text_info_list, tgt_lang)
                                add_quality(humant_dict, next_line_tokens, text_count, tgt_lang)

    list_dict = [deepl_dict, modernmt_dict, opennmt_dict, humant_dict]
    for item in list_dict:
        print(str(item))
        for key, value in item.items():
            print(key)
            for v in value:
                print(v)

    # Write sentence-level and text-level results to the output file
    out_sent = os.path.join(folder_input, domain + "_" + tgt_lang + "_sent.tab.txt")
    out_text = os.path.join(folder_input, domain + "_" + tgt_lang + "_text.tab.txt")

    with open(out_sent, "w") as fos, open(out_text, "w") as fot:
        fos.write("\t".join(["Domain", "Target Language", "Type", "Sentence", "SET", "Source", "Participant",
                            "Sentence Reading Time", "No. words sentence", "Sentence Reading Time per Word"]) + "\n")
        fot.write("\t".join(["Domain", "Target Language", "Type", "Text", "SET", "Source", "Participant",
                            "Total Reading Time (wo end)", "Total Reading Time (with end)", "No. words text", "Norm. TotReadTime (wo end)",
                             "Norm. TotReadTime (with end)", "Qanswer", "QualityScore"]) + "\n")

        print("\nWriting DeepL")
        write_to_csv(deepl_dict, fos, fot, domain, tgt_lang, "DeepL")
        print("\nWriting ModernMT")
        write_to_csv(modernmt_dict, fos, fot, domain, tgt_lang, "ModernMT")
        print("\nWriting OpenNMT")
        write_to_csv(opennmt_dict, fos, fot, domain, tgt_lang, "OpenNMT")
        print("\nWriting HT")
        write_to_csv(humant_dict, fos, fot, domain, tgt_lang, "HT")



if __name__ == '__main__':
    # Check if the folder path is provided as a command-line argument
    if len(sys.argv) != 4:
        print('Usage: python zepman_analyse_output.py <folder_path> <domain> <tgt_lang>')
        print('Example: python zapman_analyse_output.py ./output HumanMobility EN')
        sys.exit(1)

    # Get the folder path from command-line argument
    folder_path = sys.argv[1]
    domain = sys.argv[2]
    tgt_lang = sys.argv[3]

    # Call the function to analyse the files
    analyse(folder_path, domain, tgt_lang)