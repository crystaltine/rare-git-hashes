# Find your rarest git hashes!
Searches through the entire git commit history (across all branches) of a specified git repository and finds the ones with the **most letters** and the **most numbers**
- git hashes are 40 hex digits long, each one has a `10/16` chance to be a number and `6/16` to be a letter

### No dependencies! Run out-of-the-box!

Functions in `main.py` can also be imported as APIs for custom behavior, e.g. looping thru all repos in some organization/account and checking those.

### Args
```
positional arguments:
  path                       | path to git repository, or a url (add option -r to treat as url) [default: current dir]

options:
  -h, --help                 | show this help message and exit
  -r, --remote               | whether to treat <directory> as a remote repository (will clone it) [default: false]
  -k TOPK, --topk TOPK       | number of top hashes to display (for each of letters/numbers) [default 5]
  -a AUTHOR, --author AUTHOR | filter by author (git username) [default: everyone]
```

### Example
Running `python main.py -k 3` (top 6 commits on this repository):
<img width="809" height="506" alt="image" src="https://github.com/user-attachments/assets/dc036d42-d174-4050-b06c-bc84c77e8ef9" />


