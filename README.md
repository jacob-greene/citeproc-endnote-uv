# scientific-writing-endnote-workflow

This repository combines three reusable pieces for scientific writing projects:

- `citeproc-endnote`: a small Pandoc JSON filter that converts LaTeX/BibTeX citations into EndNote temporary citations in editable Word documents.
- Word citation utilities for revision workflows that start from `.docx` drafts with numbered citations and reference lists.
- Codex scientific-writing skills for drafting, editing, reviewing figures, and grant writing.

The tools are project-neutral. A thesis, manuscript, grant, or report can keep its own source files elsewhere and use this repository as the installed workflow layer.

## Install

From this repository:

```bash
uv tool install .
```

From GitHub:

```bash
uv tool install git+https://github.com/jacob-greene/citeproc-endnote-uv
```

For project-local development:

```bash
uv venv
uv pip install -e .
```

## LaTeX to Word with EndNote temporary citations

Pass a BibTeX file to the Pandoc filter explicitly:

```bash
CITEPROC_ENDNOTE_BIBLIOGRAPHY=references.bib \
  pandoc -f latex -t docx input.tex -o output.docx -F citeproc-endnote
```

The generated DOCX contains editable temporary citations such as `{Cao, 2004}`. Open the file in Word, import the matching RIS file into EndNote, then run EndNote's **Update Citations and Bibliography** command.

Convert the same BibTeX file to RIS:

```bash
bib-to-ris references.bib references.ris
```

## Word draft to EndNote-ready Word draft

For workflows that begin from a `.docx` draft with numeric superscript citations and a numbered reference list:

```bash
docx-reference-list-to-ris revised-with-reference-list.docx revised.ris
docx-numeric-to-endnote-temp revised-with-reference-list.docx revised-endnote-temp.docx
docx-word-sanity revised-endnote-temp.docx
```

`docx-reference-list-to-ris` reads the numbered reference list from the Word document and writes a matching RIS file. This is useful when a collaborator manually adds references to Word and those records need to propagate into EndNote import.

`docx-numeric-to-endnote-temp` converts numeric superscript citations such as `6,7` into EndNote temporary citations such as `{McCabe, 2012, Mutation of A677...; McCabe, 2012, EZH2 inhibition...}`. When two distinct papers share the same first author and year, the converter includes the title to make EndNote matching unique. Duplicate bibliography entries for the same paper remain concise.

By default, `docx-numeric-to-endnote-temp` removes the static reference list from the output DOCX so EndNote can regenerate the bibliography after updating citations. Use `--keep-references` if you need an inspection copy.

## EndNote import

In EndNote:

1. Open the target library.
2. Choose `File > Import > File...`.
3. Select the generated `.ris` file.
4. Set `Import Option` to `Reference Manager (RIS)` or `RIS`.
5. Import the records.
6. Open the generated DOCX in Word and run EndNote's **Update Citations and Bibliography** command.

These tools emit EndNote temporary citations, not final EndNote fields. EndNote performs the field conversion inside Word.

## Agentic revision workflow

The general workflow is documented in [docs/agentic_revision_workflow.md](docs/agentic_revision_workflow.md). The core rule is that the current commented `.docx` is the source of truth: revisions should be made only in comment-scoped regions unless the review plan explicitly justifies adjacent changes.

## Codex skills

Scientific-writing skills live in [codex-skills/](codex-skills/). Symlink the skills you want into your Codex skills directory, for example:

```bash
ln -s "$PWD/codex-skills/edit-scientific-prose" ~/.codex/skills/edit-scientific-prose
ln -s "$PWD/codex-skills/draft-scientific-paper" ~/.codex/skills/draft-scientific-paper
```

The skills are independent of the citation tools but are bundled here so a project can use one repository for prose guidance, citation conversion, and reproducible revision workflow conventions.
