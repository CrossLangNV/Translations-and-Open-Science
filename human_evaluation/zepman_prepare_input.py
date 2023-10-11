import os
import sys
import pandas as pd

def insert_eol(string):
    if len(string) <= 90:
        return string

    result = ""
    start = 0
    print('inserting eol')
    while start < len(string):
        end = min(start + 90, len(string))
        index = string.rfind(' ', start, end)
        print(start, index, end)
        print(end-start)
        if end-start == 90:
            result += string[start:index] + '\n '
            start = index   # start next segment from next character after inserted end of line
        else:
            result += string[start:end]
            start = end

    return result

def read_xlsx_files(folder_path, lang):
    """
    Reads Excel (.xlsx) files in a given folder path one by one, and reads each file row by row.

    Args:
        folder_path (str): Path of the folder containing the Excel files.
        max_words (str): Max no of words that will be used in Zepman input file
    """

    # Get all .xlsx files in the folder
    xlsx_files = [f for f in os.listdir(folder_path) if f.endswith('.xlsx')]

    # count max no. words in a text (necessary to hard-code in zepman max no. of words that will be measured
    max_char_count = 0
    max_text = ""


    # Hard-coded text that is used for the questions
    if lang == "en":
        qesttext = "You will "
        qualtext = "QUALITY ASSESSMENT"
    elif lang == "fr":
        qesttext = "Vous lirez maintenant "
        qualtext = "ÉVALUATION DE LA QUALITÉ"


    # Iterate through each .xlsx file
    for xlsx_file in xlsx_files:
        file_path = os.path.join(folder_path, xlsx_file)

        print('Reading file:', file_path)
        try:
            # Read Excel file using pandas
            df = pd.read_excel(file_path)

            # Replace "NaN" values with empty string
            df.fillna('', inplace=True)

            # Create output file name by adding the file name at the beginning and changing the extension to .txt
            output_file = os.path.splitext(xlsx_file)[0] + '.csv'
            output_file_path = os.path.join(folder_path, output_file)

            text_count = 0
            # Write contents of Excel file to tab-delimited text file with file name at the beginning
            with open(output_file_path, 'w') as f:

                #f.write(f'File Name: {xlsx_file}\n\n')
                f.write(f'### Test items ###\n')
                f.write(f'id;type;segments;question;qanswer\n')

                # Loop over each row in the DataFrame
                textcount = 0
                linecount = 0
                for index, row in df.iterrows():
                    if row[0].startswith(qesttext):
                        f.write('{};FILLER;"'.format(linecount + 1))
                        in_list_sents = row[0].strip().split('\\n')
                        for i in range(len(in_list_sents) - 1):
                            new_sent = insert_eol(in_list_sents[0].strip())
                            f.write(new_sent + "\n")
                        new_sent = insert_eol(in_list_sents[-1].strip())
                        f.write(new_sent)


                        #for sent in in_list_sents:
                            #new_sent = insert_eol(sent.strip())
                            #f.write(new_sent + "\n")
                        #new_sent = insert_eol(row[0].strip())
                        #new_line = row[0].strip().replace(".", ".\n")
                        #print(new_sent)
                        #f.write('{};FILLER;"{}";{};{}\n'.format(linecount + 1, new_sent, "", ""))
                        f.write('";;\n')
                        linecount+=1
                        continue
                    else:

                        # Write text count to file
                        if not row[0].startswith(qualtext):
                            textcount += 1
                            f.write('{};FILLER;"{}";{};{}\n'.format(linecount + 1, "TEXT_" + str(textcount), "", ""))
                        else:
                            # If its quality assessment reduce line count as we don't write TEXT_X
                            linecount -= 1

                        # Start writing the text
                        f.write('{};FILLER;"'.format(linecount + 2))
                        # Replace double quotes with single quotes for parsing the csv
                        new_line = row[0].replace('"', "'")
                        # Also replace forwards slashes with back slashes - forward slash is an indicator of when the space button is hit in zepman
                        new_line = new_line.replace("/", "\\")

                        # Print the content of each row as tab-delimited text
                        in_list_sents = new_line.strip().split('\\n')
                        in_list_sents = ['/#' + sent.strip() for sent in in_list_sents]
                        # Modify the max char count

                        # Insert end of line for max 90 chars
                        for sent in in_list_sents:
                            if len(sent) > max_char_count:
                                max_char_count = len(row[0])
                                max_text = row[0]

                            new_sent = insert_eol(sent.strip())
                            f.write(new_sent+"\n")

                        # Write end of text, question and answer
                        in_question = str(row[1])
                        in_answer = str(row[2]).lower()
                        if row[0].startswith(qualtext):
                            f.write('";' + in_question + ";" + in_answer + "\n")

                        else:
                            f.write('/#[END_OF_TEXT]";'+in_question+";"+in_answer+"\n")
                        linecount += 2



            print('Output file created:', output_file_path)


        except Exception as e:
            print(f'Error reading file {file_path}: {str(e)}')
    print("Text with max. no. words:")
    print(max_text)
    print("Max. character count = " + str(max_char_count))

if __name__ == '__main__':
    # Check if the folder path is provided as a command-line argument
    if len(sys.argv) != 3:
        print('Usage: python zepman_prepare_input.py <folder_path> <lang>')
        sys.exit(1)

    # Get the folder path from command-line argument
    folder_path = sys.argv[1]
    lang = sys.argv[2]

    # Call the function to read Excel files in the folder
    read_xlsx_files(folder_path, lang)
