import html
from pathlib import Path

import gradio as gr
import pandas as pd


DATA_FILE = Path("sample_data/final_result_lancelot.csv")


def load_alignments():
    df = pd.read_csv(DATA_FILE, sep=None, engine="python", dtype=str).fillna("")
    df = df.rename(columns={df.columns[0]: "segment_id"})
    return df


def get_segment_choices():
    df = load_alignments()
    return df["segment_id"].astype(str).tolist()


def clean_witness_name(name):
    return str(name).replace("-", " ").upper()


def view_segment(segment_id):
    df = load_alignments()

    row_match = df[df["segment_id"].astype(str) == str(segment_id)]

    if row_match.empty:
        return "<p>No segment selected.</p>"

    row = row_match.iloc[0]
    witness_columns = [col for col in df.columns if col != "segment_id"]

    if not witness_columns:
        return "<p>No witness columns found.</p>"

    main_witness = witness_columns[0]
    other_witnesses = witness_columns[1:]

    main_text = str(row[main_witness]).strip()

    html_output = f"""
<div class="reading-view">

<div class="segment-heading">
Aligned segment <span>{html.escape(str(segment_id))}</span>
</div>

<div class="main-witness-card">
<div class="witness-label">Main witness</div>
<div class="witness-meta">{html.escape(clean_witness_name(main_witness))}</div>
<div class="main-witness-text">{html.escape(main_text)}</div>
</div>

<div class="witness-section-title">Witnesses</div>

<div class="parallel-view">
"""

    for witness in other_witnesses:
        text = str(row[witness]).strip()

        if not text:
            continue

        html_output += f"""
<div class="witness-card">
<div class="witness-meta">{html.escape(clean_witness_name(witness))}</div>
<div class="witness-text">{html.escape(text)}</div>
</div>
"""

    html_output += """
</div>
</div>
"""
    return html_output


custom_css = """
html,
body,
#root,
.gradio-container,
.app,
.main,
.wrap,
.contain,
footer {
    background-color: #f7f3ec !important;
}

.gradio-container {
    max-width: 1200px !important;
    margin: auto !important;
    background: #f7f3ec !important;
    color: #2b241f !important;
}

#main-banner {
    width: 100% !important;
    max-width: 100% !important;
    height: 370px !important;
    margin-top: -20px !important;
    margin-bottom: -20px !important;
    overflow: hidden !important;
}

#main-banner img {
    width: 100% !important;
    height: 400px !important;
    object-fit: cover !important;
    display: block !important;
    transform: translate(60px) !important;
}

.tabs {
    margin-top: -25px !important;
}

/* General sections */

.card,
.about-section,
.method-section,
.explore-section,
.team-card {
    background: #f7f3ec !important;
    color: #4a3a32 !important;
    padding: 25px;
    border-radius: 18px;
    box-shadow: none !important;
    margin-bottom: 20px;
}

.about-section,
.method-section,
.explore-section {
    max-width: 980px;
    margin: 0 auto;
    padding: 34px 28px 20px 28px;
}

.about-kicker {
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-size: 13px;
    color: #9a6a45;
    margin-bottom: 10px;
    font-weight: 600;
}

.about-section h2,
.method-section h2,
.explore-section h2,
.card h2,
.team-card h2 {
    color: #8a2a22 !important;
    font-weight: 700 !important;
    font-size: 30px;
    margin-top: 8px;
    margin-bottom: 18px;
}

.about-lead {
    font-size: 18px;
    line-height: 1.6;
    margin-bottom: 14px;
}

.about-section p,
.method-section p,
.explore-section p {
    line-height: 1.65;
    margin-bottom: 18px;
}

.about-question {
    font-family: Georgia, serif;
    font-size: 22px;
    line-height: 1.45;
    color: #5a2d27;
    margin: 30px 0;
    padding-left: 22px;
    border-left: 4px solid #8a2a22;
}

.about-note,
.about-footer {
    text-align: center;
    color: #6a574e;
    font-size: 15px;
    max-width: 760px;
    margin: 30px auto 0 auto;
    background: #f7f3ec !important;
    border: none !important;
    box-shadow: none !important;
}

/* About feature blocks */

.feature-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 22px 36px;
    margin-top: 34px;
    margin-bottom: 34px;
}

.feature-card {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0;
}

.feature-title {
    color: #8a2a22;
    font-weight: 700;
    margin-bottom: 8px;
    font-size: 17px;
}

.feature-text {
    color: #4a3a32;
    font-size: 15px;
    line-height: 1.55;
}

/* Method */

.method-steps {
    margin-top: 32px;
    display: flex;
    flex-direction: column;
    gap: 18px;
}

.method-step {
    display: grid;
    grid-template-columns: 48px 1fr;
    gap: 18px;
    align-items: start;
}

.step-number {
    width: 38px;
    height: 38px;
    border-radius: 50%;
    border: 2px solid rgba(138, 42, 34, 0.35);
    color: #8a2a22;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-family: Georgia, serif;
}

.step-title {
    color: #8a2a22;
    font-weight: 700;
    font-size: 17px;
    margin-bottom: 5px;
}

.step-text {
    color: #4a3a32;
    font-size: 15px;
    line-height: 1.55;
}

/* Explore alignments */

.reading-view {
    max-width: 1080px;
    margin: 18px auto 34px auto;
}

.segment-heading {
    font-family: Georgia, serif;
    font-size: 20px;
    color: #5a2d27;
    margin-bottom: 18px;
}

.segment-heading span {
    color: #8a2a22;
    font-weight: 700;
}

.main-witness-card {
    background: #fbf8f3;
    border-left: 5px solid #8a2a22;
    padding: 22px 24px;
    margin-bottom: 28px;
    border-radius: 0 16px 16px 0;
}

.witness-label {
    color: #8a2a22;
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 8px;
}

.witness-section-title {
    color: #8a2a22;
    font-weight: 700;
    font-size: 18px;
    margin: 24px 0 10px 0;
}

.parallel-view {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    gap: 18px;
    margin-top: 18px;
    margin-bottom: 28px;
}

.witness-card {
    background: #f7f3ec;
    border-left: 3px solid rgba(138, 42, 34, 0.28);
    padding: 16px 18px;
    min-height: 120px;
}

.witness-meta {
    color: #9a6a45;
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 12px;
}

.main-witness-text {
    color: #2f2824;
    font-family: Georgia, serif;
    font-size: 20px;
    line-height: 1.7;
}

.witness-text {
    color: #2f2824;
    font-family: Georgia, serif;
    font-size: 17px;
    line-height: 1.6;
}

/* Team */

.person-avatar {
    width: 110px !important;
    height: 110px !important;
    min-height: 110px !important;
    margin: auto !important;
    display: block !important;
}

.person-avatar img {
    width: 110px !important;
    height: 110px !important;
    min-height: 110px !important;
    object-fit: cover !important;
    border-radius: 50% !important;
    border: 3px solid rgba(138, 42, 34, 0.25);
    display: block !important;
}

.person-avatar .icon-button-wrapper,
.person-avatar .image-controls,
.person-avatar [aria-label="Download"],
.person-avatar [aria-label="Fullscreen"],
.person-avatar [title="Download"],
.person-avatar [title="Fullscreen"] {
    display: none !important;
}

.person-name {
    color: #8a2a22;
    font-weight: 700;
    font-size: 17px;
    margin-top: 12px;
    margin-bottom: 8px;
    text-align: center;
}

.person-links {
    font-size: 14px;
    text-align: center;
}

.person-links a {
    color: #8a2a22 !important;
    text-decoration: none;
    font-weight: 600;
}

.person-links a:hover {
    text-decoration: underline;
}
"""


with gr.Blocks(
    title="Aquilign Demo",
    theme=gr.themes.Soft(),
    css=custom_css,
) as demo:

    gr.Image(
        value="quilign.png",
        show_label=False,
        container=False,
        elem_id="main-banner",
    )

    with gr.Tabs():

        with gr.Tab("About"):
            gr.Markdown(
                """
<div class="about-section">

<div class="about-kicker">Digital philology · Medieval texts · Multilingual alignment</div>

<h2>About Aquilign</h2>

<p class="about-lead">
<strong>Aquilign</strong> is a multilingual alignment and collation engine
for historical and philological corpora.
</p>

<p>
It is designed to help researchers compare medieval textual traditions across
languages, witnesses, translations, and corpora.
</p>

<div class="about-question">
How can we align texts copied, translated, and transformed across languages
and centuries without losing their philological depth?
</div>

<p>
Aquilign aligns parallel medieval texts at sentence or clause level, combining
rule-based segmentation with contextual methods. It is especially useful for
traditions where texts do not correspond word for word, but through adaptation,
omission, expansion, and variation.
</p>

<div class="feature-grid">
<div class="feature-card">
<div class="feature-title">Explore traditions</div>
<div class="feature-text">
Compare related textual traditions across manuscripts, languages, and versions.
</div>
</div>

<div class="feature-card">
<div class="feature-title">Align across languages</div>
<div class="feature-text">
Work with medieval Romance languages, Latin, Middle English, and other historical corpora.
</div>
</div>

<div class="feature-card">
<div class="feature-title">Discover connections</div>
<div class="feature-text">
Identify corresponding passages even when phrasing or structure diverges.
</div>
</div>

<div class="feature-card">
<div class="feature-title">Multiple witnesses & corpora</div>
<div class="feature-text">
Support research on translation, transmission, collation, and stemmatological analysis.
</div>
</div>
</div>

<p class="about-note">
Aquilign is developed within the ProMeText ecosystem and released as an
open-source research tool for computational humanities, historical linguistics,
and historical NLP.
</p>

</div>
                """
            )

        with gr.Tab("Method"):
            gr.Markdown(
                """
<div class="method-section">

<div class="about-kicker">Workflow · Segmentation · Alignment · Exploration</div>

<h2>Method</h2>

<p class="about-lead">
Aquilign is designed as a modular workflow for preparing, segmenting,
aligning, and exploring multilingual medieval textual traditions.
</p>

<div class="method-steps">

<div class="method-step">
<div class="step-number">1</div>
<div>
<div class="step-title">Prepare the texts</div>
<div class="step-text">
Input texts are gathered, cleaned, and organised by language, witness,
or textual tradition.
</div>
</div>
</div>

<div class="method-step">
<div class="step-number">2</div>
<div>
<div class="step-title">Segment into comparable units</div>
<div class="step-text">
Texts are divided into smaller units, such as sentences or clauses,
so that corresponding passages can be compared.
</div>
</div>
</div>

<div class="method-step">
<div class="step-number">3</div>
<div>
<div class="step-title">Align across languages and witnesses</div>
<div class="step-text">
Aquilign identifies related passages across texts that may differ through
translation, omission, expansion, rephrasing, or structural variation.
</div>
</div>
</div>

<div class="method-step">
<div class="step-number">4</div>
<div>
<div class="step-title">Export reusable results</div>
<div class="step-text">
Alignment results can be exported for inspection, correction, reuse,
or integration into further philological and computational workflows.
</div>
</div>
</div>

<div class="method-step">
<div class="step-number">5</div>
<div>
<div class="step-title">Explore and share</div>
<div class="step-text">
This interface focuses on making the results readable, navigable,
and easier to share with researchers and collaborators.
</div>
</div>
</div>

</div>

<p class="about-note">
The current demo presents pre-computed alignments. Future versions can connect
this interface more directly to Aquilign output files and interactive visualisations.
</p>

</div>
                """
            )

        with gr.Tab("Explore alignments"):
            segments = get_segment_choices()
            first_segment = segments[0] if segments else None

            gr.Markdown(
                """
<div class="explore-section">

<div class="about-kicker">Browse · Compare · Inspect</div>

<h2>Explore alignments</h2>

<p class="about-lead">
Browse pre-computed alignments produced with Aquilign. Each aligned segment
can be read across a main witness and its corresponding witnesses.
</p>

</div>
                """
            )

            segment_selector = gr.Dropdown(
                choices=segments,
                value=first_segment,
                label="Aligned segment",
                interactive=True,
            )

            parallel_output = gr.HTML(
                value=view_segment(first_segment) if first_segment else "<p>No data found.</p>"
            )

            segment_selector.change(
                fn=view_segment,
                inputs=segment_selector,
                outputs=parallel_output,
            )

            with gr.Accordion("Full alignment table", open=False):
                gr.Dataframe(
                    value=load_alignments(),
                    interactive=False,
                )

        with gr.Tab("Team"):
            gr.Markdown(
                """
<div class="card team-card">

<div class="about-kicker">People behind the project</div>

## Our team

Aquilign is developed by a small interdisciplinary team working at the intersection
of medieval studies, philology, computational humanities, and multilingual NLP.

</div>
                """
            )

            with gr.Row():
                with gr.Column():
                    gr.Image(
                        value="team/matthias.png",
                        show_label=False,
                        container=False,
                        elem_classes="person-avatar",
                    )
                    gr.Markdown(
                        """
<div class="person-name">Matthias Gille Levenson</div>
<div class="person-links">
<a href="https://orcid.org/0000-0001-9488-5986" target="_blank">ORCID</a>
</div>
                        """
                    )

                with gr.Column():
                    gr.Image(
                        value="team/lucence.png",
                        show_label=False,
                        container=False,
                        elem_classes="person-avatar",
                    )
                    gr.Markdown(
                        """
<div class="person-name">Lucence Ing</div>
<div class="person-links">
<a href="https://orcid.org/0000-0002-8742-3000" target="_blank">ORCID</a>
</div>
                        """
                    )

                with gr.Column():
                    gr.Image(
                        value="team/carola.png",
                        show_label=False,
                        container=False,
                        elem_classes="person-avatar",
                    )
                    gr.Markdown(
                        """
<div class="person-name">Carolina Macedo</div>
<div class="person-links">
<a href="https://orcid.org/0009-0001-5972-0921" target="_blank">ORCID</a>
</div>
                        """
                    )

            gr.Markdown(
                """
<div class="about-footer">
Together, the team works toward making multilingual medieval textual traditions
easier to compare, explore, and share.
</div>
                """
            )

        with gr.Tab("Contact"):
            gr.Markdown(
                """
<div class="card">

## Contact

For questions about Aquilign, please open an issue on GitHub.

GitHub repository: `ProMeText/Aquilign`

</div>
                """
            )


demo.launch(allowed_paths=["team"])
