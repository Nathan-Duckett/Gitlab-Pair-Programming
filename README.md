# Gitlab-Pair-Programming Matrix

This is a basic utility to traverse a specified project to find out the pair combinations assigned to tickets to create a pair programming matrix.
This is used to find out which groups of people have worked together the most and record who should be assigned together more for group work during University courses.

Some assumptions have been made to ignore listings of issues which contain all team members at once.

All issues must be within milestones to be counted within this method. Anything not in a milestone will be ignored. This assumes that milestones are of reasonable size to get all of the content.

## Usage

You will need a `config.yaml` file which can be set from the `template.config.yaml` example.

This contains:

```yaml
rootURI: Your gitlab instance API endpoint e.g. https://gitlab.com/api/v4/
PAT: A generated Personal Access Token with API access level
projectID: The project ID number you want this to interface with.
```

Then you can run the command

```sh
python3 track_pairs.py
```

This will use the configuration and output a markdown formatted table with pair counts into STDOUT.

## Uploading to Gitlab

You can either manually copy the output from STDOUT into a Gitlab Wiki page which contains the pair programming or matrix or you can make use of the tool [Gitlab-Wiki-Updater](https://github.com/Nathan-Duckett/Gitlab-Wiki-Updater) using the `upload.py -s WIKI_SLUG` option you can pipe the output from this tool straight into a wiki page.

For example using:

```python
python3 track_pairs.py | python3 upload.py -s Pair-Programming-Matrix
```

Where **Pair-Programming-Matrix** points to the Gitlab Wiki slug this is stored inside.