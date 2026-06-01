
# Aquilign Explorer

Interactive Gradio explorer for reviewed and raw Aquilign alignments of multilingual medieval textual traditions.

Aquilign Explorer provides a public interface for browsing alignment outputs produced with [Aquilign](https://github.com/ProMeText/Aquilign). It is designed as a lightweight demo and reading interface for medievalists, philologists, computational humanities researchers, and collaborators who want to inspect multilingual alignments without installing the full Aquilign pipeline.

## Overview

This interface allows users to explore alignment tables produced with Aquilign. It currently supports demo corpora from:

- *Lancelot en prose*
- *De regimine principum*

For each corpus, the interface can display both:

- **Reviewed alignments**: curated alignment samples manually reviewed for demonstration purposes.
- **Raw alignments**: automatic Aquilign output provided for transparency.

The first witness in each alignment table is treated as the **main witness**. Other columns are displayed as corresponding witnesses or textual versions.

## Features

- Browse multilingual alignment tables by corpus
- Switch between reviewed and raw Aquilign output
- Read a main witness alongside corresponding witnesses
- Navigate between aligned segments
- Search across witnesses
- Choose which witnesses to display
- Download the current dataset
- View the full alignment table
- Report alignment issues through GitHub
- Access related publications, datasets, and repositories

## Run locally

- Clone the repository

```bash
git clone git@github.com:carolisteia/aquilign-explorer.git
cd aquilign-explorer
```

- Launch the interface:

```bash
python app.py
```
- Then open the local Gradio URL in youy browser


