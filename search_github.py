import requests
import json
from main import get_rarest

# put github PATs in here
# format:
# {
#   "gh": "ghp_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
#   "gh2": "ghp_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
#   ...
# }
#
API_KEYS = json.load(open("./apikeys.json"))

CONFIGS = [
    {
        "apiurl": "https://github.com/api/graphql", # should be graphql endpoint
        "apitoken": API_KEYS["gh"],
        "orgname": "something",
        "base_repo_url": "github.com"
    },
]

MAIN_AUTHORS_LIST = [
    None, # everyone (no filter)
]

def gql_query(cursor: str | None, orgname: str):
    PER_FETCH = 100
    return f"""
        {{
            organization(login: "{orgname}") {{
                repositories(first: {PER_FETCH},{f', after: \"{cursor}\"' if cursor else ''}) {{
                    nodes {{
                        name
                    }}
                    pageInfo {{
                        hasNextPage
                        endCursor
                    }}
                }}
            }}
        }}
    """

def run(
    apiurl: str, 
    apitoken: str, 
    orgname: str, 
    base_repo_url: str, 
    authors_list: list[str | None],
    outfile: str,
):
    all_top_1_letters = {
        author_name:[] for author_name in authors_list
    }
    all_top_1_numbers = {
        author_name:[] for author_name in authors_list
    }

    next_cursor = None
    has_next_cursor = True

    _i = 0
    while has_next_cursor:
        res = requests.post(
            apiurl, 
            headers={'Authorization': f'Bearer {apitoken}'},
            data=json.dumps({'query': gql_query(next_cursor, orgname)})
        )

        resjson = res.json()
        
        if not resjson.get("data"):
            print(f"\x1b[31m--- REQUEST FAILED ??? ---")
            print(resjson)
            continue

        data = resjson["data"]["organization"]["repositories"]
        next_cursor = data["pageInfo"]["endCursor"]
        has_next_cursor = data["pageInfo"]["hasNextPage"]

        print(f"org repos request completed, got {len(data["nodes"])} repos")
        for repo in data["nodes"]:
            _i += 1
            reponame = repo["name"]
            repourl = f"{base_repo_url}:{orgname}/{reponame}.git"
            
            print(f"#{_i} - {reponame}:")
            for _raw_authorname in authors_list:
                authorname = _raw_authorname if _raw_authorname is not None else "<everyone>"
                try:
                    top_letters, top_numbers = get_rarest(repourl, remote=True, topk=1, author=authorname, verbose=False)
                except Exception as e:
                    print(f"\x1b[31m  {authorname}: skipping due to exception: {e}\x1b[0m")
                    all_top_1_letters[_raw_authorname].append((reponame, None))
                    all_top_1_numbers[_raw_authorname].append((reponame, None))
                    continue
                
                if len(top_letters) == 0:
                    # no commits...
                    print(f"\x1b[2m  {authorname}: has no commits\x1b[0m")
                    all_top_1_letters[_raw_authorname].append((reponame, None))
                    all_top_1_numbers[_raw_authorname].append((reponame, None))

                else:
                    top_1_letter = top_letters[0]
                    top_1_number = top_numbers[0]
                    all_top_1_letters[_raw_authorname].append((reponame, top_1_letter))
                    all_top_1_numbers[_raw_authorname].append((reponame, top_1_number))
                    
                    print(f"  {authorname}:")
                    print(f"    {top_1_letter.hashstr} (\x1b[33m{top_1_letter.n_letters}\x1b[0m) (1 in \x1b[31m{round(1/top_1_letter.prob_letters):,}\x1b[0m)")
                    print(f"    {top_1_number.hashstr} (\x1b[33m{top_1_number.n_numbers}\x1b[0m) (1 in \x1b[31m{round(1/top_1_number.prob_numbers):,}\x1b[0m)")

        if not has_next_cursor:
            with open(outfile, "a") as f:
                print(f"\x1b[34m=== {orgname} final bests ===")
                f.write(f"=== {orgname} final bests ===\n")
                for _raw_authorname in authors_list:
                    authorname = _raw_authorname if _raw_authorname is not None else "<everyone>"
                    all_top_1_letters[_raw_authorname].sort(key=lambda entry: entry[1].n_letters if entry[1] else 0)
                    all_top_1_numbers[_raw_authorname].sort(key=lambda entry: entry[1].n_numbers if entry[1] else 0)

                    top_1_letter_repo, top_1_letter = all_top_1_letters[_raw_authorname][-1]
                    top_1_number_repo, top_1_number = all_top_1_numbers[_raw_authorname][-1]
                    
                    print(f"\x1b[33m{authorname}:\x1b[0m")
                    f.write(f"{authorname}:\n")
                    
                    if top_1_letter:
                        authorstr = f" by {top_1_letter.author}" if (authorname is None and top_1_letter is not None) else ""
                        resultstr = f"  {top_1_letter.hashstr} ({top_1_letter.n_letters} let) in {top_1_letter_repo}{authorstr} (1 in {round(1/top_1_letter.prob_letters):,})"
                        print(resultstr)
                        f.write(resultstr + "\n")
                    else:
                        resultstr = "  no commits"
                        print(f"\x1b[2m{resultstr}\x1b[0m")
                        f.write(resultstr + "\n")

                    if top_1_number:
                        authorstr = f" by {top_1_number.author}" if (authorname is None and top_1_number is not None) else ""
                        resultstr = f"  {top_1_number.hashstr} ({top_1_number.n_numbers} num) in {top_1_number_repo}{authorstr} (1 in {round(1/top_1_number.prob_numbers):,})"
                        print(resultstr)
                        f.write(resultstr + "\n")
                    else:
                        resultstr = "  no commits"
                        print(f"\x1b[2m{resultstr}\x1b[0m")
                        f.write(resultstr + "\n")

            break

if __name__ == "__main__":
    from time import time
    outfile = f"./search_results_{round(time())}.txt"

    for config in CONFIGS:
        print(f"\x1b[34m===== running search: {config['orgname']} =====\x1b[0m")
        run(config["apiurl"], config["apitoken"], config["orgname"], config["base_repo_url"], MAIN_AUTHORS_LIST, outfile)