# Find your rarest git hashes!
Searches through the entire git commit history (across all branches) of a specified git repository and finds the ones with the **most letters** and the **most numbers**.

Git hashes are 40 hex digits long, each one has a `10/16` chance to be a number and `6/16` to be a letter

## Example
Running `python main.py -k 3` (top 6 commits on this repository):
<img width="809" height="506" alt="image" src="https://github.com/user-attachments/assets/dc036d42-d174-4050-b06c-bc84c77e8ef9" />

## No dependencies! Run out-of-the-box!
Functions in `main.py` can also be imported as APIs and fully support custom behavior, e.g. looping thru all repos in some organization/account and checking those.

## Args
```
positional arguments:
  path                       | path to git repository, or a url (add option -r to treat as url) [default: current dir]

options:
  -h, --help                 | show this help message and exit
  -r, --remote               | whether to treat <directory> as a remote repository (will clone it) [default: false]
  -k TOPK, --topk TOPK       | number of top hashes to display (for each of letters/numbers) [default 5]
  -a AUTHOR, --author AUTHOR | filter by author (git username) [default: everyone]
```

## Sample Runs
Some more sample runs on popular large repositories, as of 8 March 2026:

[Linux](https://github.com/torvalds/linux): 
```
#1 Letters: cafcfcaa60dbb5bcccbbc1d0ad7d4bdeeb4d0cc8 - 30 letters (0.0001579%) (1 in 633,236)
  by Al Viro on 2006-01-12 09:08:53 -0800
  message: "[PATCH] sh: task_thread_info()"

#1 Numbers: 287774414568010855642518513f085491644061 - 39 numbers (0.0000171%) (1 in 5,846,007)
  by H. Peter Anvin on 2008-02-04 16:47:57 +0100
  message: "x86: use _ASM_EXTABLE macro in arch/x86/lib/usercopy_32.c"
```

[Rust](https://github.com/rust-lang/rust):
```
#1 Letters: 26babaafcdbcfdf2e842d84dbeabbed0dae6efef - 30 letters (0.0001579%) (1 in 633,236)
  by bors on 2013-05-20 12:04:47 -0700
  message: "auto merge of #6559 : jbclements/rust/hygiene-fns-and-cleanup, r=jbclements"

#1 Numbers: 107807d3932c2765580725604802f76935239723 - 37 numbers (0.0016694%) (1 in 59,901)
  by Jack Wrenn on 2024-03-15 17:55:49 +0000
  message: "Safe Transmute: lowercase diagnostics"
```

[Tensorflow](https://github.com/tensorflow/tensorflow):
```
#1 Letters: 8ce8dbdb8edcdbfaebcc632ccfbbbaebb83dcee7 - 31 letters (0.0000297%) (1 in 3,367,262)
  by Adrian Kuegel on 2025-06-12 03:06:49 -0700
  message: "Remove unused ForwardsValue hook (NFC)."

#1 Numbers: 172363f62c7025862018127850b2305279256635 - 37 numbers (0.0016694%) (1 in 59,901)
  by Jeremy Lau on 2019-12-11 14:02:58 -0800
  message: "Temporarily disable failing test."
```

[Vscode](https://github.com/microsoft/vscode):
```
#1 Letters: 11eefc95cbdeafb6525f88bbbaabc8afadaeaa0f - 28 letters (0.0030882%) (1 in 32,381)
  by aamunger on 2023-03-14 16:38:37 -0700
  message: "fixed alias"

#1 Numbers: 2f908943a1376995023558735692217428367043 - 38 numbers (0.0002092%) (1 in 477,927)
  by Johannes on 2022-09-06 11:16:08 +0200
  message: "have an explicit `SnippetTextEdit` and all to set them onto a workspace edit"
```

## Probabilities

Some sample probabilities below:

| N | >= N Numbers | >= N Letters |
|---|--------------|--------------|
| 25 | 1 in 2 | 1 in 856 |
| 26 | 1 in 2 | 1 in 2,591 |
| 27 | 1 in 3 | 1 in 8,684 |
| 28 | 1 in 5 | 1 in 32,381 |
| 29 | 1 in 8 | 1 in 135,000 |
| 30 | 1 in 15 | 1 in 633,236 |
| 31 | 1 in 30 | 1 in 3,367,262 |
| 32 | 1 in 71 | 1 in 20,488,889 |
| 33 | 1 in 191 | 1 in 144,337,407 |
| 34 | 1 in 598 | 1 in 1,195,086,837 |
| 35 | 1 in 2,233 | 1 in 11,864,389,076 |
| 36 | 1 in 10,232 | 1 in 145,167,966,504 |
| 37 | 1 in 59,901 | 1 in 2,278,943,913,106 |
| 38 | 1 in 477,927 | 1 in 48,932,941,835,856 |
| 39 | 1 in 5,846,007 | 1 in 1,615,751,276,481,490 |
| 40 | 1 in 146,150,164 | 1 in 109,332,503,041,914,112 |
