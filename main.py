import os
import subprocess
import heapq
import argparse
import tempfile

# utils n stuff

class TopkHandler:
	""" minheap basically, ensures length is always at most k """
	def __init__(self, k: int):
		self.k = k
		self.heap = []

	def at_capacity(self) -> bool:
		return len(self.heap) >= self.k

	def get_minval(self) -> int:
		return 0 if len(self.heap) == 0 else self.heap[0][0]

	def add_thing(self, thing: tuple) -> None: # heap key should be [0]
		if len(self.heap) < self.k:
			heapq.heappush(self.heap, thing)
		else:
			heapq.heappushpop(self.heap, thing)

def get_commit_message(commit_hash: str) -> str:
	""" returns the commit message for a given commit hash """
	try:
		subp_cmd = ['git', 'log', '-n', '1', '--pretty=%s', commit_hash]
		message = subprocess.check_output(subp_cmd).decode('utf-8').strip()
		return message
	except subprocess.CalledProcessError as e:
		print(f"\x1b[31merror: {e}\x1b[0m")
		return ""

def ellipsisize_text(text: str, max_len: int = 80) -> str:
	""" returns text truncated to max_len with ellipsis (...) if it exceeds `max_len` """
	if len(text) > max_len:
		return text[:max_len - 3] + '...'
	return text

# (len 41)
# >= 0 letters -> >= 41 letters (equiv. <= 40 nums -> <= -1 nums), hardcoded cuz idgaf
PROBS = [1, 0.9999999931577225, 0.9999998289430587, 0.9999979076314924, 0.9999833056635884, 0.999902264741721, 0.9995521679592538, 0.9983268292206189, 0.9947558420394541, 0.9859176487660712, 0.9670628364495212, 0.931992885540738, 0.8746056931445474, 0.7913942641700711, 0.6838594944184401, 0.5594264037058385, 0.4300159893647329, 0.3086937259199464, 0.20592663217848023, 0.12713852697668945, 0.07240152757334008, 0.037917217949229975, 0.018211898164024208, 0.008000959729872126, 0.0032062582042702795, 0.0011685100558894946, 0.00038601476691127326, 0.00011515101303419666, 3.088228960577282e-05, 7.407430936426176e-06, 1.5791901633470091e-06, 2.9697719326959257e-07, 4.880694099654422e-08, 6.928210925467301e-09, 8.367592787652037e-10, 8.428584005494473e-11, 6.888572073318082e-12, 4.3879974151586167e-13, 2.0436130804366296e-14, 6.18907139084941e-16, 9.14641092243755e-18, 0]

def commits_from_remote(url: str, author: str | None) -> dict:
	""" clone the repo at `url` into an (automatically cleaned up) temp dir """
	global tempdir
	tempdir = tempfile.TemporaryDirectory()
	subprocess.run(['git', 'clone', url, tempdir.name, '--filter=blob:none', '--bare'])
	return commits_from_local(tempdir.name, author)

def commits_from_local(project_dir: str, author: str | None) -> dict:
	os.chdir(project_dir)

	try:
		# git log --pretty=format:%H %ci %an %B --all
		subp_cmd = ['git', 'log', '--pretty=format:%H %ci %an']
		if author is not None:
			subp_cmd.insert(2, f'--author={author}')
		commits = subprocess.check_output(subp_cmd)

	except subprocess.CalledProcessError as e:
		print(f"\x1b[31merror: {e}\x1b[0m")
		exit(1)

	commits_listified = commits.decode('utf-8').split('\n')
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

# --- interface: ---

def check_args(args: dict) -> None:
	if not args.remote:
		if not os.path.isdir(args.path):
			# local repo doesnt exist
			print(f"\x1b[31merror: invalid directory \"{args.path}\". maybe use \"-r\" if this is a url?\x1b[0m")
			exit(1)
	else:
		# no url provided
		if not args.path:
			print(f"\x1b[31merror: url must be provided for remote repo\x1b[0m")
			exit(1)

	if args.topk <= 0:
		# need to list at least 1 top commit
		print(f"\x1b[31merror: k must be a positive integer (got {args.topk})\x1b[0m")
		exit(1)

def main():
	
	parser = argparse.ArgumentParser(description="finds the rarest commit hashes in a repository by count of numbers/letters in their 40-digit hash")
	parser.add_argument("path", help="path to git repository, or a url (add option -r to treat as url) [default: current dir]", default=os.path.dirname(os.path.realpath(__file__)), nargs="?")
	#parser.add_argument("-i", "--interactive", help="use interactive mode (pass options through stdin) [default: false]", default=False, store="store_true")
	parser.add_argument("-r", "--remote", help="whether to treat <directory> as a remote repository (will clone it) [default: false]", default=False, action="store_true")
	parser.add_argument("-k", "--topk", type=int, help="number of top hashes to display (for each of letters/numbers) [default 5]", default=5)
	parser.add_argument("-a", "--author", type=str, help="filter by author (git username) [default: everyone]", default=None)
	args = parser.parse_args()

	check_args(args)

	compiled_commit_info = commits_from_local(args.path, args.author) if not args.remote else commits_from_remote(args.path, args.author)

	by_author_string = f' by \x1b[33m{args.author}\x1b[0m' if args.author else ''
	if len(compiled_commit_info) < 1 or "" in compiled_commit_info:
		# probably means no commits found due to invalid/nonexistent author
		print(f"\nno commits found{by_author_string} in \x1b[33m{args.path}\x1b[0m!")
		exit(0)

	print(f"\ntotal unique commits{by_author_string} in \x1b[33m{args.path}\x1b[0m: {len(compiled_commit_info)}")

	topk_letters = TopkHandler(args.topk)
	topk_numbers = TopkHandler(args.topk)

	print()

	_i = 0
	for hsh in compiled_commit_info:
		print(f"checking #{_i+1}/{len(compiled_commit_info)} ({100*(_i+1)/len(compiled_commit_info):.2f}%)", end='\r\x1b[0m')
		_i += 1
		letters_ct = sum(c.isalpha() for c in hsh)
		numbers_ct = 40 - letters_ct

		if letters_ct >= topk_letters.get_minval() or not topk_letters.at_capacity():
			topk_letters.add_thing((letters_ct, hsh))

		if numbers_ct >= topk_numbers.get_minval() or not topk_numbers.at_capacity():
			topk_numbers.add_thing((numbers_ct, hsh))

	# prune leaderboards to get top k. these arent too big so sorting is fine lol
	real_topk_letters = sorted(topk_letters.heap, key=lambda x: x[0], reverse=True)
	real_topk_numbers = sorted(topk_numbers.heap, key=lambda x: x[0], reverse=True)

	print(f"\n\ntop {args.topk} most letters:")
	for i in range(len(real_topk_letters)):
		n_letters, hsh = real_topk_letters[i]
		fmt_msg = ellipsisize_text(get_commit_message(hsh)).replace('\n', ' ')
		prob = PROBS[n_letters]
		print(f"#{i+1}: \x1b[34m{hsh}\x1b[0m - {n_letters} letters ({prob*100:_.7f}%) (1 in \x1b[31m{round(1/prob):,}\x1b[0m)")
		print(f"  by \x1b[33m{compiled_commit_info[hsh]['author']}\x1b[0m on \x1b[33m{compiled_commit_info[hsh]['date']}\x1b[0m")
		print(f"  message: \"{fmt_msg}\"")

	print(f"\ntop {args.topk} most numbers:")
	for i in range(len(real_topk_numbers)):
		n_numbers, hsh = real_topk_numbers[i]
		fmt_msg = ellipsisize_text(get_commit_message(hsh)).replace('\n', ' ')
		prob = 1 - PROBS[41 - n_numbers]
		print(f"#{i+1}: \x1b[34m{hsh}\x1b[0m - {n_numbers} numbers ({prob*100:_.7f}%) (1 in \x1b[31m{round(1/prob):,}\x1b[0m)")
		print(f"  by \x1b[33m{compiled_commit_info[hsh]['author']}\x1b[0m on \x1b[33m{compiled_commit_info[hsh]['date']}\x1b[0m")
		print(f"  message: \"{fmt_msg}\"")

	print(f"\n\x1b[2m(probabilities calculated for x or more letters/numbers)\x1b[0m")
	# print(f"\x1b[2mrun 'git show --format=%B -s <commit-hash>' to check commit messages!\x1b[0m")

if __name__ == "__main__":
	main()
