# Publishing To A Study Hub

Use this reference when the user wants the generated study sheet to live inside a reusable library repo.

## Model

The study hub is a separate Git repository from the skill repo.

It is designed to start private and optionally become a GitHub template repository later.

The skill does not create the GitHub repo automatically in v1. It publishes into a local clone that already exists.

## Expected repo shape

The publisher expects:

```text
study-sheet-hub-template/
├── .study-hub.json
├── index.html
└── library/
    └── catalog.json
```

`library/catalog.json` is the source of truth for the hub index.

## Bootstrap locally

Seed a new repo from the bundled asset:

```bash
cp -R skills/general/txt-to-html-srs/assets/study-hub-template /path/to/study-sheet-hub-template
cd /path/to/study-sheet-hub-template
git init
git add .
git commit -m "Initialize study hub template"
```

## Optional GitHub creation

If the user wants to create the private GitHub repo after bootstrapping locally, a minimal path is:

```bash
gh repo create study-sheet-hub-template --private --source=. --push
```

After the repo exists, the user can mark it as a template repository in GitHub settings.

GitHub docs referenced for this model:
- [Creating a repository from a template](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-repository-from-a-template)
- [Creating a template repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-template-repository)

## Publish command

Use the deterministic publisher instead of editing the hub by hand:

```bash
python skills/general/txt-to-html-srs/scripts/publish_to_hub.py \
  --hub-dir /path/to/hub-clone \
  --html /path/to/generated-study-sheet.html
```

Optional flags:
- `--commit` to create a local commit
- `--push` to push after committing
- `--title`, `--summary`, `--tag`, `--source-kind` to override embedded metadata when needed

## Operational rules

- Require explicit user intent before publishing.
- Require explicit user intent before pushing.
- Prefer the metadata embedded in `study-sheet-data`.
- Let the publisher manage slug collisions.
- Treat `.study-hub.json` as the compatibility contract.

## Failure cases

Stop instead of guessing when:
- `.study-hub.json` is missing
- `schema_version` is incompatible
- `library/catalog.json` is invalid JSON
- the target is not a local clone of the intended hub repo
