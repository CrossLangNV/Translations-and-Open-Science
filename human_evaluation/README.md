# Scripts

## Process TSV

Convert raw TSV data into src and trg files, grouped per document.

Usage:

```bash
python process_tsv.py <tsv filename> createdocs <outdir>
```

## Label Studio (MQM annotations) - Prepare the import files
Convert src/trg file pairs into a single file for MQM error annotation with LabelStudio.
Use also the corresponding term list to mark terms in the source segments.

Usage:
```bash
python labelstudio_prepare_input.py <folder_src-ref> <folder_deepl> <folder_opennmt> <folder_modernmt> <folder_output>
```

## Label Studio (MQM annotations) - Analyse the output
Step 1: Collect error annotations per MT engine using the random MT order (MT log file), json output from LabelStudio and input files created.
Produces a new JSON file. 

Usage: 
```bash
python labelstudio_collect_annotations_from_json.py <json_output> <folder_input> <file_mt_log>
```

Step2: Analyse the collected annotations (JSON) in Step 1

Usage: 
```bash
python labelstudio_analyse_annotations.py <folder_input>'
```

## Zepman - Prepare the input files (self-paced reading)
- requires the input xlsx files, produces csv files to be used with Zepman

Usage:
```bash
python zepman_prepare_input.py <folder_path>
```

## Zepman - Analyse the output (self-paced reading)
- requires the input xlsx files and the csv export files from zepman in the same folder
- tgt_lang: EN or FR
- domain: Can be defined by the user

Usage:
```bash
python zepman_analyse_output.py <folder_path> <domain> <tgt_lang>
```

## Correlation analysis

Usage:
```python
from util_evaluation_correlation import correlation, correlation2
x = [1, 2, 3, 4, 5]
y = [2, 2, 1, 3, 5]
r = correlation(x, y)
R = correlation2(x, y)
kappa = cohen_
r == R
```