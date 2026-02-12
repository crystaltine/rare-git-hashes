from typing import List, Tuple
from dataclasses import dataclass
import os
import subprocess
import heapq
import argparse
import tempfile

# heapq got maxheap stuff in py 3.14
HEAPQ_HAS_MAXHEAP = hasattr(heapq, "heapify_max") and hasattr(heapq, "heappop_max")

# (len 41) [>= 0 letters -> >= 41 letters] (equiv. <= 40 nums -> <= -1 nums), hardcoded cuz idgaf
PROBS = [1, 0.9999999931577225, 0.9999998289430587, 0.9999979076314924, 0.9999833056635884, 0.999902264741721, 0.9995521679592538, 0.9983268292206189, 0.9947558420394541, 0.9859176487660712, 0.9670628364495212, 0.931992885540738, 0.8746056931445474, 0.7913942641700711, 0.6838594944184401, 0.5594264037058385, 0.4300159893647329, 0.3086937259199464, 0.20592663217848023, 0.12713852697668945, 0.07240152757334008, 0.037917217949229975, 0.018211898164024208, 0.008000959729872126, 0.0032062582042702795, 0.0011685100558894946, 0.00038601476691127326, 0.00011515101303419666, 3.088228960577282e-05, 7.407430936426176e-06, 1.5791901633470091e-06, 2.9697719326959257e-07, 4.880694099654422e-08, 6.928210925467301e-09, 8.367592787652037e-10, 8.428584005494473e-11, 6.888572073318082e-12, 4.3879974151586167e-13, 2.0436130804366296e-14, 6.18907139084941e-16, 9.14641092243755e-18, 0]

__verbose = False

# --- utils ---

def _log(msgtype: str, text: str) -> None:
	if not __verbose:
		return
	
	match msgtype:
		case "error": 
			return print(f"\x1b[31merror:\x1b[0m {text}\x1b[0m")
		case "warning": 
			return print(f"\x1b[33mwarning:\x1b[0m {text}\x1b[0m")
		case "info": 
			return print(f"\x1b[36minfo:\x1b[0m {text}\x1b[0m")
		case _:
			return print(f"{msgtype}: {text}\x1b[0m")		

def get_commit_message(commit_hash: str) -> str:
	""" returns the commit message for a given commit hash """
	try:
		subp_cmd = ['git', 'log', '-n', '1', '--pretty=%s', commit_hash]
		message = subprocess.check_output(subp_cmd).decode('utf-8', errors="ignore").strip()
		return message
	except subprocess.CalledProcessError as e:
		_log("error", f"failed to get commit message for {commit_hash}: {e}")
		return ""

def ellipsisize_text(text: str, max_len: int = 80) -> str:
	""" returns text truncated to max_len with ellipsis (...) if it exceeds `max_len` """
	if len(text) > max_len:
		return text[:max_len - 3] + '...'
	return text

def commits_from_local(project_dir: str, author: str | None) -> dict:
	os.chdir(project_dir)

	try:
		_log("info", "logging commits...")
		subp_cmd = ['git', 'log', '--pretty=format:%H %ci %an']
		if author is not None:
			subp_cmd.insert(2, f'--author={author}')
		commits = subprocess.check_output(subp_cmd)

	except subprocess.CalledProcessError as e:
		_log("error", f"failed to log commits: {e}")
		raise e

	commits_listified = commits.decode('utf-8', errors="ignore").split('\n')
	compiled_commit_info = dict()
	for commit_info in commits_listified:
		if commit_info.strip() == "": # this sometimes happens cuz git adds 2 newlines sometimes, but not always?????
			continue
		hsh, date, time, tz, author = commit_info.split(" ", 4)
		compiled_commit_info[hsh] = {
			'date': f"{date} {time} {tz}",
			'author': author.strip(),
		}

	return compiled_commit_info

def commits_from_remote(url: str, author: str | None) -> dict:
	""" clone the repo at `url` into an (automatically cleaned up) temp dir """
	_log("info", f"temporarily cloning remote repo {url}...")
	global tempdir
	tempdir = tempfile.TemporaryDirectory()

	try:
		subprocess.run(
			['git', 'clone', url, tempdir.name, '--filter=blob:none', '--bare'], 
			capture_output=(not __verbose),
			check=True
		)
	except subprocess.CalledProcessError as e:
		_log("error", f"failed to clone from {url}: exit code {e.returncode}")
		raise e

	return commits_from_local(tempdir.name, author)

# --- api ---

@dataclass
class RareCommitInfo:
	hashstr: str
	""" 40-hex-digit hash of the commit """
	n_letters: int
	""" number of letters out of 40 in the hash. """
	n_numbers: int
	""" number of digits out of 40 in the hash """
	prob_letters: float
	""" probability of getting n_letters or more """
	prob_numbers: float
	""" probability of getting n_numbers or more """
	author: str
	""" author name attached to the commit """
	datetime: str
	""" string of the date of the commit in the format `1999-12-31 00:00:00 -0800` """
	message: str
	""" commit message, not truncated """

def get_rarest(
	path: str, 
	remote: bool, 
	topk: int, 
	author: str = None, 
	verbose: bool = None
) -> Tuple[List[RareCommitInfo], List[RareCommitInfo]]:
	""" fetches the `topk` top commits for both most letters and numbers. Returns (list of top letters, list of top numbers) """
	
	# this is supposed to be the api entrypoint so setting verbose here is fine 
	global __verbose
	if verbose is not None:
		__verbose = verbose

	compiled_commit_info = commits_from_local(path, author) if not remote else commits_from_remote(path, author)

	by_author_string = f' by \x1b[33m{author}\x1b[0m' if author else ''
	if len(compiled_commit_info) < 1 or "" in compiled_commit_info:
		_log("info", f"no commits found{by_author_string} in \x1b[33m{path}\x1b[0m!")
		return ([], [])

	_log("info", f"total unique commits{by_author_string} in \x1b[33m{path}\x1b[0m: {len(compiled_commit_info)}")
	_log("info", "searching for rarest...")

	# top letters
	if HEAPQ_HAS_MAXHEAP:
		# py >= 3.14
		letter_counts = [(sum(c.isalpha() for c in hsh), hsh) for hsh in compiled_commit_info]
		heapq.heapify_max(letter_counts)
	else:
		letter_counts = [(-sum(c.isalpha() for c in hsh), hsh) for hsh in compiled_commit_info]
		heapq.heapify(letter_counts)

	# to be returned...
	returnval = ([], [])

	# using heappop for letters, we gotta add them back afterward to reheapify for numbers
	top_letters = []

	for _ in range(min(topk, len(letter_counts))):
		if HEAPQ_HAS_MAXHEAP:
			n_letters, hsh = heapq.heappop_max(letter_counts)
			top_letters.append((n_letters, hsh))
		else: 
			n_letters, hsh = heapq.heappop(letter_counts)
			top_letters.append((n_letters, hsh))
			n_letters *= -1

		prob_letters = PROBS[n_letters]
		n_numbers = 40 - n_letters
		prob_numbers = 1 - PROBS[41 - n_numbers]

		returnval[0].append(RareCommitInfo(
			hsh, 
			n_letters, n_numbers,
			prob_letters, prob_numbers, 
			compiled_commit_info[hsh]['author'], 
			compiled_commit_info[hsh]['date'], 
			get_commit_message(hsh)
		))
	
	# re-populate for nums finding
	letter_counts.extend(top_letters)
	if not HEAPQ_HAS_MAXHEAP:
		# positive-ify so that letter_counts is back to correct, then we can just minheap it
		letter_counts = list(map(lambda x: -x, letter_counts))

	heapq.heapify(letter_counts)

	for _ in range(min(topk, len(letter_counts))):
		n_letters, hsh = heapq.heappop(letter_counts)
		prob_letters = PROBS[n_letters]
		n_numbers = 40 - n_letters
		prob_numbers = 1 - PROBS[41 - n_numbers]

		returnval[1].append(RareCommitInfo(
			hsh, 
			n_letters, n_numbers,
			prob_letters, prob_numbers, 
			compiled_commit_info[hsh]['author'], 
			compiled_commit_info[hsh]['date'], 
			get_commit_message(hsh)
		))

	return returnval

# --- interface: ---

def check_args(args) -> None:
	if not args.remote:
		if not os.path.isdir(args.path):
			# local repo doesnt exist
			_log("error", f"invalid directory \"{args.path}\". maybe add -r if this is a url?")
			raise FileNotFoundError(f"invalid directory \"{args.path}\". maybe add -r if this is a url?")
	else:
		# no url provided
		if not args.path:
			_log("error", "url must be provided for remote repo")
			raise ValueError("url must be provided for remote repo")

	if args.topk <= 0:
		# need to list at least 1 top commit
		_log("error", f"k must be a positive integer (got {args.topk})")
		raise ValueError(f"k must be a positive integer (got {args.topk})")

def main():
	global __verbose 
	__verbose = True
	
	parser = argparse.ArgumentParser(description="finds the rarest commit hashes in a repository by count of numbers/letters in their 40-digit hash")
	parser.add_argument("path", help="path to git repository, or a url (add option -r to treat as url) [default: current dir]", default=os.path.dirname(os.path.realpath(__file__)), nargs="?")
	#parser.add_argument("-i", "--interactive", help="use interactive mode (pass options through stdin) [default: false]", default=False, store="store_true")
	parser.add_argument("-r", "--remote", help="whether to treat <directory> as a remote repository (will clone it) [default: false]", default=False, action="store_true")
	parser.add_argument("-k", "--topk", type=int, help="number of top hashes to display (for each of letters/numbers) [default 5]", default=5)
	parser.add_argument("-a", "--author", type=str, help="filter by author (git username) [default: everyone]", default=None)
	args = parser.parse_args()
	
	try:
		check_args(args)
		top_letters, top_numbers = get_rarest(args.path, args.remote, args.topk, args.author)
	except:
		exit(1)

	print(f"\ntop {args.topk} most letters:")
	for i in range(len(top_letters)):
		commit = top_letters[i]
		fmt_msg = ellipsisize_text(commit.message).replace('\n', ' ')

		print(f"#{i+1}: \x1b[34m{commit.hashstr}\x1b[0m - {commit.n_letters} letters ({commit.prob_letters*100:_.7f}%) (1 in \x1b[31m{round(1/commit.prob_letters):,}\x1b[0m)")
		print(f"  by \x1b[33m{commit.author}\x1b[0m on \x1b[33m{commit.datetime}\x1b[0m")
		print(f"  message: \"{fmt_msg}\"")

	print(f"\ntop {args.topk} most numbers:")
	for i in range(len(top_numbers)):
		commit = top_numbers[i]
		fmt_msg = ellipsisize_text(commit.message).replace('\n', ' ')

		print(f"#{i+1}: \x1b[34m{commit.hashstr}\x1b[0m - {40-commit.n_letters} numbers ({commit.prob_numbers*100:_.7f}%) (1 in \x1b[31m{round(1/commit.prob_numbers):,}\x1b[0m)")
		print(f"  by \x1b[33m{commit.author}\x1b[0m on \x1b[33m{commit.datetime}\x1b[0m")
		print(f"  message: \"{fmt_msg}\"")

	print(f"\n\x1b[2m(probabilities calculated for x or more letters/numbers)\x1b[0m")

if __name__ == "__main__":
	main()
