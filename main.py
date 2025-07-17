import os
import subprocess

# utils n stuff

def get_commit_info(_hash: str) -> dict:
	"""
	Returns dict({
		'author': str,
		'date': str,
		'message': str,
	})
	"""
	info = {}
	try:
		# git show -s --pretty=%an <commit-hash>
		get_author_cmd = ['git', 'show', '-s', '--pretty=%an', _hash]

		# git show --no-patch --format=%ci <commit-hash>
		get_date_cmd = ['git', 'show', '--no-patch', '--format=%ci', _hash]

		# git show --format=%B -s <commit-hash>
		get_message_cmd = ['git', 'show', '--format=%B', '-s', _hash]
	
		info['author'] = subprocess.check_output(
			get_author_cmd,
			stderr=subprocess.DEVNULL,
			shell=True
		).decode('utf-8').strip()
		info['date'] = subprocess.check_output(
			get_date_cmd,
			stderr=subprocess.DEVNULL,
			shell=True
		).decode('utf-8').strip()
		info['message'] = subprocess.check_output(			
			get_message_cmd,
			stderr=subprocess.DEVNULL,
			shell=True
		).decode('utf-8').strip()

		return info

	except subprocess.CalledProcessError as e:
	  print(f"\x1b[31mError while getting commit info for {_hash}: {e}")

# (len 42)
# 0 letters or more -> 41 letters or more, hardcoded cuz idgaf
PROBS = [1, 0.9999999931577225, 0.9999998289430587, 0.9999979076314924, 0.9999833056635884, 0.999902264741721, 0.9995521679592538, 0.9983268292206189, 0.9947558420394541, 0.9859176487660712, 0.9670628364495212, 0.931992885540738, 0.8746056931445474, 0.7913942641700711, 0.6838594944184401, 0.5594264037058385, 0.4300159893647329, 0.3086937259199464, 0.20592663217848023, 0.12713852697668945, 0.07240152757334008, 0.037917217949229975, 0.018211898164024208, 0.008000959729872126, 0.0032062582042702795, 0.0011685100558894946, 0.00038601476691127326, 0.00011515101303419666, 3.088228960577282e-05, 7.407430936426176e-06, 1.5791901633470091e-06, 2.9697719326959257e-07, 4.880694099654422e-08, 6.928210925467301e-09, 8.367592787652037e-10, 8.428584005494473e-11, 6.888572073318082e-12, 4.3879974151586167e-13, 2.0436130804366296e-14, 6.18907139084941e-16, 9.14641092243755e-18, 0]

AUTHOR_EVERYONE = "<everyone>"
THIS_DIR = os.path.dirname(os.path.realpath(__file__))

#####################

PROJECT_DIR = input(f"absolute path of git repo (directory) to check \x1b[33m(enter to use {THIS_DIR})\x1b[0m: ")

if PROJECT_DIR == "": # use dir of this file
	PROJECT_DIR = THIS_DIR
elif not os.path.isdir(PROJECT_DIR):
	print("\x1b[31mInvalid directory\x1b[0m")
	exit(1)
print(f"Checking directory: \x1b[35m{PROJECT_DIR}\x1b[0m")

COMMIT_AUTHOR = input("which commit author or git username? \x1b[33m(press enter for everyone)\x1b[0m: ")
COMMIT_AUTHOR = COMMIT_AUTHOR if COMMIT_AUTHOR != "" else AUTHOR_EVERYONE
print(f"Checking commits by: \x1b[35m{COMMIT_AUTHOR}\x1b[0m")

all_shas = {}
os.chdir(PROJECT_DIR)

try:
	subp_cmd = ['git', 'log', '--pretty=format:%H', '--all']
	if COMMIT_AUTHOR != AUTHOR_EVERYONE:
		subp_cmd.insert(2, f'--author={COMMIT_AUTHOR}')

	shas = subprocess.check_output(
		subp_cmd,
		stderr=subprocess.DEVNULL,
		shell=True
	)
except subprocess.CalledProcessError as e:
  print(f"\x1b[31mError: {e}")

shas_list = shas.decode('utf-8').split('\n')
all_shas.update({(hsh, PROJECT_DIR) for hsh in shas_list})

print(f"\ntotal UNIQUE commits by \x1b[35m{COMMIT_AUTHOR}\x1b[0m in {PROJECT_DIR}: {len(all_shas)}")

print()

most_letters_hash = None
most_letters_hash_num = 0
most_numbers_hash = None
most_numbers_hash_num = 0

for hsh in all_shas:
	letters = sum(c.isalpha() for c in hsh)
	numbers = sum(c.isdigit() for c in hsh)

	if letters > most_letters_hash_num:
		most_letters_hash_num = letters
		most_letters_hash = hsh

	if numbers > most_numbers_hash_num:
		most_numbers_hash_num = numbers
		most_numbers_hash = hsh

most_letters_prob = PROBS[most_letters_hash_num]
most_numbers_prob = 1 - PROBS[40 - most_numbers_hash_num]

info_for_most_letters = get_commit_info(most_letters_hash)
info_for_most_numbers = get_commit_info(most_numbers_hash)

print(f"Most letters: {most_letters_hash_num}/40 - \x1b[34m{most_letters_hash}\x1b[0m\x1b[33m ({most_letters_prob*100:_.12f}%)\x1b[0m")
print(f"\tby \x1b[33m{info_for_most_letters['author']}\x1b[0m on \x1b[33m{info_for_most_letters['date']}\x1b[0m")
# print(f"\"{info_for_most_letters['message']}\"")

print()

print(f"Most numbers: {most_numbers_hash_num}/40 - \x1b[34m{most_numbers_hash}\x1b[0m\x1b[33m ({most_numbers_prob*100:_.12f}%)\x1b[0m")
print(f"\tby \x1b[33m{info_for_most_numbers['author']}\x1b[0m on \x1b[33m{info_for_most_numbers['date']}\x1b[0m")
#print(f"\"{info_for_most_numbers['message']}\"")

print()

print(f"probabilities calculated for x or more letters/numbers.")
print(f"run \x1b[33mgit show --format=%B -s \x1b[34m<commit-hash>\x1b[0m to check commit messages!")