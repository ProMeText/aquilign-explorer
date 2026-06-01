[![Hugging Face Space](https://img.shields.io/badge/Live%20demo-Hugging%20Face-yellow)](https://huggingface.co/spaces/ProMeText/aquilign-explorer)
[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)

# Aquilign Explorer

Interactive Gradio explorer for reviewed and raw Aquilign alignments of multilingual medieval textual traditions.

Aquilign Explorer provides a public interface for browsing alignment outputs produced with [Aquilign](https://github.com/ProMeText/Aquilign). It is designed as a lightweight demo and reading interface for medievalists, philologists, computational humanities researchers, and collaborators who want to inspect multilingual alignments without installing the full Aquilign pipeline.

[Open the live demo on Hugging Face Spaces](https://huggingface.co/spaces/ProMeText/aquilign-explorer)
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
git clone git@github.com:ProMeText/aquilign-explorer.git
cd aquilign-explorer
```

- Launch the interface:

```bash
python app.py
```
- Then open the local Gradio URL in your browser


## Citation

If you use Aquilign Explorer, the demo alignments, or the associated datasets, please cite the relevant publications and resources.

### Aquilign / Lancelot alignments


Gille Levenson, M., Ing, L., & Camps, J.-B. (2024). Textual Transmission without Borders: Multiple Multilingual Alignment and Stemmatology of the *Lancelot en prose* (Medieval French, Castilian, Italian). In W. Haverals, M. Koolen, & L. Thompson (Eds.), *Proceedings of the Computational Humanities Research Conference 2024* (Vol. 3834, pp. 65–92). CEUR.

- CEUR entry: https://ceur-ws.org/Vol-3834/#paper104
- PDF: https://ceur-ws.org/Vol-3834/paper104.pdf


### Segmentation dataset

Ing, L., Gille Levenson, M., & Macedo, C. (2025). *Multilingual Segmentation Dataset for Historical Prose (13th–16th c.)* (Version 1.0) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.16992629

### Segmentation workflow

Ing, L., Gille Levenson, M., & Macedo, C. (2026). Phrase-level segmentation on medieval corpora for aligning multilingual texts. In *Proceedings of the Fifteenth Language Resources and Evaluation Conference (LREC 2026)*. https://doi.org/10.63317/32HUZUUOKPFR


## License

This repository, including the demo interface, alignment tables, corpus excerpts, and associated documentation, is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License (CC BY-NC-SA 4.0).

Reuse requires appropriate citation of the relevant publications and resources listed in the Citation section.
