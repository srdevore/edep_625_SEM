# Commands

Handy commands for maintaining this repo.

## Get the Python virtualenv out of git

`.venv/` was missing from `.gitignore`, so commit `70600e3` captured ~8,200
virtualenv files. It was never pushed, so a plain reset fixes it.

Undo the commit, keeping every file change on disk. Never use `--hard`, which
would discard the edits:

```{bash}
git reset --mixed HEAD~1
```

Confirm the venv is now ignored instead of tracked (should print a rule):

```{bash}
git check-ignore -v .venv/bin/activate
```

Re-stage and review the list (expect project files only, no `.venv`):

```{bash}
git add . && git status --short
```

Re-commit:

```{bash}
git commit -m "updates file download to reflect lecture"
```

Verify the venv is gone from history (expect `0`, then no output):

```{bash}
git ls-tree -r HEAD --name-only | grep -c "^\.venv/"
git log --oneline --all -- .venv
```

Do this before pushing. Once a commit with `.venv` reaches the remote,
removing it needs a published-history rewrite (`git filter-repo`) instead.

## Render the teacher version of a deck

Renders slides with teacher-only content included; press `S` for speaker notes:

```{bash}
quarto render lectures/test_lecture.qmd --profile teacher
```

## Refresh lecture download links

Rewrites each deck's `description:` link from its own filename, so the
"Download" column always matches the lecture. Quarto runs this automatically on
render; run it directly to check the result:

```{bash}
Rscript pre-render.R && grep -n "^description:" lectures/*.qmd
```
