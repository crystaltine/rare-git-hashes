import os
import subprocess

# utils n stuff

def get_commit_message(commit_hash: str) -> str:
	""" returns the commit message for a given commit hash """
	try:
		subp_cmd = ['git', 'show', '--format=%B', '-s', commit_hash]
		message = subprocess.check_output(subp_cmd).decode('utf-8').strip()
		return message
	except subprocess.CalledProcessError as e:
		print(f"\x1b[31merror: {e}\x1b[0m")
		return ""

def ellipsisize_text(text: str, max_len: int = 50) -> str:
	""" returns text truncated to max_len with ellipsis (...) if it exceeds `max_len` """
	if len(text) > max_len:
		return text[:max_len - 3] + '...'
	return text

# (len 41)
# 0 letters or more -> 40 letters or more, hardcoded cuz idgaf
PROBS = [1, 0.9999999931577225, 0.9999998289430587, 0.9999979076314924, 0.9999833056635884, 0.999902264741721, 0.9995521679592538, 0.9983268292206189, 0.9947558420394541, 0.9859176487660712, 0.9670628364495212, 0.931992885540738, 0.8746056931445474, 0.7913942641700711, 0.6838594944184401, 0.5594264037058385, 0.4300159893647329, 0.3086937259199464, 0.20592663217848023, 0.12713852697668945, 0.07240152757334008, 0.037917217949229975, 0.018211898164024208, 0.008000959729872126, 0.0032062582042702795, 0.0011685100558894946, 0.00038601476691127326, 0.00011515101303419666, 3.088228960577282e-05, 7.407430936426176e-06, 1.5791901633470091e-06, 2.9697719326959257e-07, 4.880694099654422e-08, 6.928210925467301e-09, 8.367592787652037e-10, 8.428584005494473e-11, 6.888572073318082e-12, 4.3879974151586167e-13, 2.0436130804366296e-14, 6.18907139084941e-16, 9.14641092243755e-18]

DEFAULT_TOP_K = 5
AUTHOR_EVERYONE = "<everyone>"
THIS_DIR = os.path.dirname(os.path.realpath(__file__))

def main():
	project_dir = input(f"absolute path of git repo (directory) to check \x1b[33m(leave empty to use {THIS_DIR})\x1b[0m: ").strip()
	project_dir = project_dir if project_dir != "" else THIS_DIR
	if not os.path.isdir(project_dir):
		print(f"\x1b[31merror: invalid directory \"{project_dir}\"\x1b[0m")
		exit(1)
	print(f"  checking directory: \x1b[35m{project_dir}\x1b[0m!")

	commit_author = input("which commit author or git username? \x1b[33m(leave empty for everyone)\x1b[0m: ").strip()
	commit_author = commit_author if commit_author != "" else AUTHOR_EVERYONE
	print(f"  checking commits by: \x1b[35m{commit_author}\x1b[0m!")

	top_k = input(f"get the top how many hashes? \x1b[33m(leave empty for {DEFAULT_TOP_K})\x1b[0m: ").strip()
	if top_k != "":
		try:
			top_k = int(top_k)
			if top_k <= 0:
				raise ValueError()
		except ValueError:
			top_k = DEFAULT_TOP_K
			print(f">>> invalid positive integer provided, using default...")
	else:
		top_k = DEFAULT_TOP_K

	print(f"  fetching top \x1b[35m{top_k}\x1b[0m hashes with most letters/numbers\x1b[0m!")

	compiled_commit_info = {}
	os.chdir(project_dir)

	shas = ...
	try:
		# git log --pretty=format:%H %ci %an %B --all
		subp_cmd = [
			'git', 'log', '--pretty=format:%H %ci %an', '--all'
		]
		if commit_author != AUTHOR_EVERYONE:
			subp_cmd.insert(2, f'--author=\"{commit_author}\"')

		commits = subprocess.check_output(subp_cmd)
	except subprocess.CalledProcessError as e:
		print(f"\x1b[31merror: {e}\x1b[0m")
		exit(1)

	commits_listified = commits.decode('utf-8').split('\n')

	for commit_info in commits_listified:
		if commit_info.strip() == "": # this sometimes happens cuz git adds 2 newlines sometimes, but not always?????
			continue
		hsh, date, time, tz, author = commit_info.split(" ", 4)
		compiled_commit_info[hsh] = {
			'date': f"{date} {time} {tz}",
			'author': author.strip(),
		}

	if len(compiled_commit_info) < 1 or "" in compiled_commit_info:
		# probably means no commits found due to invalid/nonexistent author
		print(f"\nno commits found by \x1b[33m{commit_author}\x1b[0m in \x1b[33m{project_dir}\x1b[0m!")
		exit(0)

	print(f"\ntotal unique commits by \x1b[33m{commit_author}\x1b[0m in \x1b[33m{project_dir}\x1b[0m: {len(compiled_commit_info)}")

	topk_letters = [] # will store tuples of (hash, letters)
	topk_numbers = [] # will store tuples of (hash, numbers)

	# current minimum "specialness" to qualify for the leaderboards
	# lazy - we will sort and take the top k at the end
	curr_min_letters = 0
	curr_min_numbers = 0

	print()

	_i = 0
	for hsh in compiled_commit_info:
		print(f"checking #{_i+1}/{len(compiled_commit_info)} ({100*_i/len(compiled_commit_info):.2f}%) \x1b[2mdebug: top letters len {len(topk_letters)} (min {curr_min_letters}), top numbers len {len(topk_numbers)} (min {curr_min_numbers})", end='\r\x1b[0m')
		_i += 1
		letters_ct = sum(c.isalpha() for c in hsh)
		numbers_ct = 40 - letters_ct

		if letters_ct >= curr_min_letters:
			topk_letters.append((hsh, letters_ct))
			if len(topk_letters) >= top_k: # leaderboard getting too full raise the bar!!!!!!
				curr_min_letters = max(topk_letters, key=lambda x: x[1])[1]

		if numbers_ct >= curr_min_numbers:
			topk_numbers.append((hsh, numbers_ct))
			if len(topk_numbers) >= top_k:
				curr_min_numbers = max(topk_numbers, key=lambda x: x[1])[1]

	# prune leaderboards to get top k
	topk_letters.sort(key=lambda x: x[1], reverse=True)
	real_topk_letters = topk_letters[:top_k]

	topk_numbers.sort(key=lambda x: x[1], reverse=True)
	real_topk_numbers = topk_numbers[:top_k]

	print(f"\n\ntop {top_k} most letters:")
	for i in range(len(real_topk_letters)):
		hsh, n_letters = real_topk_letters[i]
		fmt_msg = ellipsisize_text(get_commit_message(hsh), 50).replace('\n', ' ')
		prob = PROBS[n_letters]
		print(f"#{i+1}: \x1b[34m{hsh}\x1b[0m - {n_letters} letters ({prob*100:_.7f}%)\x1b[0m")
		print(f"  by \x1b[33m{compiled_commit_info[hsh]['author']}\x1b[0m on \x1b[33m{compiled_commit_info[hsh]['date']}\x1b[0m")
		print(f"  \"{fmt_msg}\"")

	print(f"\ntop {top_k} most numbers:")
	for i in range(len(real_topk_numbers)):
		hsh, n_numbers = real_topk_numbers[i]
		fmt_msg = ellipsisize_text(get_commit_message(hsh), 50).replace('\n', ' ')
		prob = 1 - PROBS[40 - n_numbers]
		print(f"#{i+1}: \x1b[34m{hsh}\x1b[0m - {n_numbers} numbers ({prob*100:_.7f}%)\x1b[0m")
		print(f"  by \x1b[33m{compiled_commit_info[hsh]['author']}\x1b[0m on \x1b[33m{compiled_commit_info[hsh]['date']}\x1b[0m")
		print(f"  \"{fmt_msg}\"")

	print(f"\x1b[2mprobabilities calculated for x or more letters/numbers.\x1b[0m")
	# print(f"\x1b[2mrun 'git show --format=%B -s <commit-hash>' to check commit messages!\x1b[0m")

if __name__ == "__main__":
	main()
