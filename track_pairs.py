import json
import requests
import sys
import yaml
from collections import Counter 
from os import path

file_dir = path.dirname(path.abspath(__file__))


def load_config():
    """Load yaml config"""
    with open(f"{file_dir}/config.yaml") as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)
        return config

def get_milestones():
    """Get all of the milestones for the configured project"""
    return _get(f"projects/{config['projectID']}/milestones")

def get_issues(params={}):
    """Get all of the issues from the configured project"""
    return _get(f"projects/{config['projectID']}/issues", params)

def _get(uriEnd, params={}):
    """Basic helper function to make a GET request to the Gitlab API with specified parameters and endpoint"""
    res = requests.get(f"{config['rootURI']}{uriEnd}",
                        headers={"PRIVATE-TOKEN": config['PAT']},
                        params=params)

    if (res.status_code == 200):
        json_string = res.content.decode("utf-8")
        return json.loads(json_string)
    else:
        return res.status_code

def process_pairs(contents):
    """Process through the contents to return all pairs assigned to an issue"""
    pairs = []
    for issue in contents:
        if len(issue['assignees']) == 2:
            pair = []
            for assignee in issue['assignees']:
                pair.append(assignee['name'])
            pairs.append(pair)

    return pairs

def process_multi(contents):
    """Process through the contents to return all groups greater than 2 on an issue"""
    groups = []
    for issue in contents:
        if len(issue['assignees']) > 2:
            group = []
            for assignee in issue['assignees']:
                group.append(assignee['name'])
            groups.append(group)

    return groups

def count_pairs(total_pairs, names=[], count=[]):
    """
    Count up all of the pairings into a 2D array defined by names matching to their pairing within count.
    This will create a dynamic 2D array of size names * names. Duplicate values will intersect where
    [a][b] == [b][a] within this array.

    total_pairs is the extracted pair array flattened from the repo
    """
    countedGroups = Counter([tuple(i) for i in total_pairs])
    for entry in countedGroups.most_common():
        # Ensure names are added to names list
        for name in entry[0]:
            if name not in names:
                fill = [0]
                for i in range(len(names)):
                    count[i].append(0)
                    fill.append(0)
                names.append(name)
                count.append(fill)
        value = entry[1]
        leftName = names.index(entry[0][0])
        rightName = names.index(entry[0][1])
        count[leftName][rightName] += value
        count[rightName][leftName] += value
    
    return names, count


def count_groups(total_multi, names=[], count=[]):
    """
    Count up all of the group pairings into a 2D array defined by names matching to their pairing within count.
    This can either create a 2D array of size names * names or can build on to an existing names, and count array.
    Duplicate values will intersect where [a][b] == [b][a] within these arrays.

    total_multi is the extracted group pairing array flattened from the repo
    """
    countedGroups = Counter([tuple(i) for i in total_multi])
    print(countedGroups)
    for entry in countedGroups.most_common():
        # Ensure names are added to names list
        for name in entry[0]:
            if name not in names:
                fill = [0]
                for i in range(len(names)):
                    count[i].append(0)
                    fill.append(0)
                names.append(name)
                count.append(fill)

        # Skip if all members are present (assumes that all members are already within the recordings)
        if len(entry[0]) == len(names):
            continue

        value = entry[1]
        i = 1
        for name in entry[0]:
            leftName = names.index(name)
            j = i
            while j < len(entry[0]):
                rightName = names.index(entry[0][j])
                count[leftName][rightName] += value
                count[rightName][leftName] += value
                j += 1
            i += 1
    
    return names, count


def print_md_table(names, counts):
    """Print out a neatly formatted table from the specified names and pairing counts"""
    nameStr = "| |"
    sepStr = "|---|"
    for name in names:
        nameStr += f" {name} |"
        sepStr += "-----|"

    print(nameStr)
    print(sepStr)
    i = 0
    for c in counts:
        rowStr = "|"
        rowStr += f" {names[i]} |"
        for ic in c:
            if ic != 0:
                rowStr += f" {ic} |"
            else:
                rowStr += " |"

        print(rowStr)
        i += 1


config = load_config()
def main():
    """ 
    Main method for the application to launch, collect pairs, and groups
    calculate and output a MD table
    """
    milestones = get_milestones()
    total_pairs = []
    total_multi = []
    for milestone in milestones:
        contents = get_issues({'milestone': milestone['title']})
        pairs = process_pairs(contents)
        multi = process_multi(contents)
        # Flatten pairs into 2D array from 3D array
        for pair in pairs:
            total_pairs.append(pair)
        # Flatten groups into 2D array from 3D array
        for m in multi:
            total_multi.append(m)
    
    names, count = count_pairs(total_pairs)
    names, count = count_groups(total_multi, names, count)
    print_md_table(names, count)

if __name__ == '__main__':
    main()