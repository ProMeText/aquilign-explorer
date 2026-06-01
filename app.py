import html
import urllib.parse
from pathlib import Path

import gradio as gr
import pandas as pd


DATASETS = {
    "Lancelot": {
        "Reviewed": Path("sample_data/reviewed_lancelot.csv"),
        "Raw": Path("sample_data/raw_lancelot.csv"),
    },
    "De regimine principum": {
        "Reviewed": Path("sample_data/reviewed_de_regimine.csv"),
        "Raw": Path("sample_data/raw_de_regimine.csv"),
    },
}


def get_data_file(corpus_name, alignment_type):
    return DATASETS[corpus_name][alignment_type]


def load_alignments(corpus_name, alignment_type):
    data_file = get_data_file(corpus_name, alignment_type)

    if not data_file.exists():
        return pd.DataFrame({"segment_id": []})

    df = pd.read_csv(data_file, sep=None, engine="python", dtype=str).fillna("")
    df = df.rename(columns={df.columns[0]: "segment_id"})
    return df


def get_segment_choices(corpus_name, alignment_type):
    df = load_alignments(corpus_name, alignment_type)

    if df.empty:
        return []

    return df["segment_id"].astype(str).tolist()


def search_segments(corpus_name, alignment_type, query):
    df = load_alignments(corpus_name, alignment_type)

    if df.empty:
        return []

    if query is None or not str(query).strip():
        return df["segment_id"].astype(str).tolist()

    query = str(query).strip().lower()
    matching_segments = []

    for _, row in df.iterrows():
        row_text = " ".join(str(value).lower() for value in row.values)

        if query in row_text:
            matching_segments.append(str(row["segment_id"]))

    return matching_segments


def get_witness_choices(corpus_name, alignment_type):
    df = load_alignments(corpus_name, alignment_type)

    if df.empty:
        return []

    witness_columns = [col for col in df.columns if col != "segment_id"]

    if len(witness_columns) <= 1:
        return []

    return witness_columns[1:]


def clean_witness_name(name):
    return str(name).replace("-", " ").upper()


def view_segment(corpus_name, alignment_type, segment_id, selected_witnesses=None):
    df = load_alignments(corpus_name, alignment_type)

    if df.empty:
        return "<p>No data found for this corpus and alignment type.</p>"

    row_match = df[df["segment_id"].astype(str) == str(segment_id)]

    if row_match.empty:
        return "<p>No segment selected.</p>"

    row = row_match.iloc[0]
    witness_columns = [col for col in df.columns if col != "segment_id"]

    if not witness_columns:
        return "<p>No witness columns found.</p>"

    main_witness = witness_columns[0]
    other_witnesses = witness_columns[1:]

    if selected_witnesses:
        other_witnesses = [w for w in other_witnesses if w in selected_witnesses]

    main_text = str(row[main_witness]).strip()

    warning = ""
    if alignment_type == "Raw":
        warning = """
<div class="raw-warning">
Raw Aquilign output is shown for transparency. It may contain alignment errors
and should not be considered manually validated scholarly alignment.
</div>
"""

    html_output = f"""
<div class="reading-view">

{warning}

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


def corpus_notice(corpus_name, alignment_type):
    df = load_alignments(corpus_name, alignment_type)

    if df.empty:
        return """
<div class="corpus-notice">
No data found for this corpus.
</div>
"""

    witness_columns = [col for col in df.columns if col != "segment_id"]
    segment_count = len(df)
    witness_count = len(witness_columns)

    return f"""
<div class="corpus-notice">
<strong>{html.escape(corpus_name)}</strong> · {html.escape(alignment_type)} alignments<br>
{segment_count} aligned segments · {witness_count} witnesses / textual versions
</div>
"""


def get_download_file(corpus_name, alignment_type):
    data_file = get_data_file(corpus_name, alignment_type)

    if data_file.exists():
        return gr.update(value=str(data_file))

    return gr.update(value=None)


def make_issue_report(corpus_name, alignment_type, segment_id):
    if not segment_id:
        return ""

    return f"""Corpus: {corpus_name}
Alignment type: {alignment_type}
Segment: {segment_id}

Describe the alignment issue here:
"""


def make_github_issue_link(corpus_name, alignment_type, segment_id):
    if not segment_id:
        return ""

    title = f"Alignment issue: {corpus_name}, segment {segment_id}"
    body = make_issue_report(corpus_name, alignment_type, segment_id)

    url = (
        "https://github.com/ProMeText/Aquilign/issues/new?"
        + urllib.parse.urlencode({"title": title, "body": body})
    )

    return f"""
<div class="report-box">
<a href="{url}" target="_blank">Open a GitHub issue for this segment</a>
</div>
"""


def update_explore(corpus_name, alignment_type):
    df = load_alignments(corpus_name, alignment_type)
    segments = get_segment_choices(corpus_name, alignment_type)
    witnesses = get_witness_choices(corpus_name, alignment_type)

    if not segments:
        return (
            gr.update(choices=[], value=None),
            "",
            gr.update(choices=[], value=[]),
            "<p>No data found.</p>",
            df,
            corpus_notice(corpus_name, alignment_type),
            get_download_file(corpus_name, alignment_type),
            "",
            "",
        )

    first_segment = segments[0]

    return (
        gr.update(choices=segments, value=first_segment),
        "",
        gr.update(choices=witnesses, value=witnesses),
        view_segment(corpus_name, alignment_type, first_segment, witnesses),
        df,
        corpus_notice(corpus_name, alignment_type),
        get_download_file(corpus_name, alignment_type),
        make_issue_report(corpus_name, alignment_type, first_segment),
        make_github_issue_link(corpus_name, alignment_type, first_segment),
    )


def update_search(corpus_name, alignment_type, query, selected_witnesses):
    segments = search_segments(corpus_name, alignment_type, query)

    if not segments:
        return (
            gr.update(choices=[], value=None),
            "<p>No matching segment found.</p>",
            '<div class="search-status">No matching segment found. Clear the search to return to the full corpus.</div>',
            "",
            "",
        )

    first_segment = segments[0]

    search_status = ""
    if query and str(query).strip():
        search_status = f"""
<div class="search-status">
Search results for <strong>{html.escape(str(query))}</strong>: {len(segments)} matching segment(s).
Use the segment menu or Previous / Next to browse them.
</div>
"""

    return (
        gr.update(choices=segments, value=first_segment),
        view_segment(corpus_name, alignment_type, first_segment, selected_witnesses),
        search_status,
        make_issue_report(corpus_name, alignment_type, first_segment),
        make_github_issue_link(corpus_name, alignment_type, first_segment),
    )


def clear_search(corpus_name, alignment_type, selected_witnesses):
    segments = get_segment_choices(corpus_name, alignment_type)

    if not segments:
        return (
            gr.update(value=""),
            gr.update(choices=[], value=None),
            "<p>No data found.</p>",
            "",
            "",
            "",
        )

    first_segment = segments[0]

    return (
        gr.update(value=""),
        gr.update(choices=segments, value=first_segment),
        view_segment(corpus_name, alignment_type, first_segment, selected_witnesses),
        "",
        make_issue_report(corpus_name, alignment_type, first_segment),
        make_github_issue_link(corpus_name, alignment_type, first_segment),
    )


def move_segment(corpus_name, alignment_type, current_segment, query, selected_witnesses, direction):
    segments = search_segments(corpus_name, alignment_type, query)

    if not segments:
        return (
            gr.update(choices=[], value=None),
            "<p>No segment available.</p>",
            "",
            "",
        )

    current_segment = str(current_segment)

    if current_segment in segments:
        current_index = segments.index(current_segment)
    else:
        current_index = 0

    if direction == "previous":
        new_index = max(0, current_index - 1)
    else:
        new_index = min(len(segments) - 1, current_index + 1)

    new_segment = segments[new_index]

    return (
        gr.update(choices=segments, value=new_segment),
        view_segment(corpus_name, alignment_type, new_segment, selected_witnesses),
        make_issue_report(corpus_name, alignment_type, new_segment),
        make_github_issue_link(corpus_name, alignment_type, new_segment),
    )


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
    font-size: 18px;
    line-height: 1.45;
    color: #5a2d27;
    margin: 38px 0 70px 0;;
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

.raw-warning {
    background: #fbf8f3;
    border-left: 4px solid #9a6a45;
    padding: 14px 18px;
    margin-bottom: 22px;
    color: #5a4a42;
    font-size: 15px;
    line-height: 1.5;
}

.corpus-notice {
    max-width: 980px;
    margin: 0 auto 20px auto;
    padding: 16px 20px;
    background: #fbf8f3;
    border-left: 4px solid rgba(138, 42, 34, 0.45);
    color: #4a3a32;
    font-size: 15px;
    line-height: 1.5;
}

.search-status {
    max-width: 980px;
    margin: 8px auto 20px auto;
    padding: 12px 16px;
    background: #fbf8f3;
    border-left: 4px solid #9a6a45;
    color: #5a4a42;
    font-size: 14px;
    line-height: 1.5;
}

.report-box {
    margin-top: 12px;
    padding: 12px 16px;
    background: #fbf8f3;
    border-left: 4px solid rgba(138, 42, 34, 0.35);
}

.report-box a {
    color: #8a2a22 !important;
    font-weight: 700;
    text-decoration: none;
}

.report-box a:hover {
    text-decoration: underline;
}

/* Gradio form controls */

.gradio-container label,
.gradio-container .wrap label,
.gradio-container span {
    color: #8a2a22 !important;
}

.gradio-container input,
.gradio-container textarea,
.gradio-container select {
    background: #f7f3ec !important;
    color: #2b241f !important;
    border-color: rgba(138, 42, 34, 0.18) !important;
}

.gradio-container .block,
.gradio-container .form,
.gradio-container .form > *,
.gradio-container [data-testid="block-info"],
.gradio-container [data-testid="dropdown"] {
    background: #f7f3ec !important;
    border-color: rgba(138, 42, 34, 0.12) !important;
}

.gradio-container button {
    background: #f7f3ec !important;
    color: #8a2a22 !important;
    border-color: rgba(138, 42, 34, 0.18) !important;
}
/* Witness checkbox chips */

.gradio-container input[type="checkbox"] {
    accent-color: #8a2a22 !important;
}

.gradio-container label:has(input[type="checkbox"]) {
    background: #f7f3ec !important;
    color: #4a3a32 !important;
    border: 1px solid rgba(138, 42, 34, 0.18) !important;
    border-radius: 10px !important;
}

.gradio-container label:has(input[type="checkbox"]:checked) {
    background: #fbf8f3 !important;
    color: #8a2a22 !important;
    border: 1px solid rgba(138, 42, 34, 0.35) !important;
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
/* Contact */

.contact-section {
    max-width: 980px;
    margin: 0 auto;
    padding: 34px 28px 20px 28px;
    color: #4a3a32;
}

.contact-section h2 {
    color: #8a2a22 !important;
    font-weight: 700 !important;
    font-size: 30px;
    margin-top: 8px;
    margin-bottom: 18px;
}

.contact-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 22px;
    margin-top: 30px;
    margin-bottom: 28px;
}

.contact-card {
    background: #f7f3ec;
    border-left: 3px solid rgba(138, 42, 34, 0.35);
    padding: 18px;
}

.contact-title {
    color: #8a2a22;
    font-weight: 700;
    font-size: 17px;
    margin-bottom: 8px;
}

.contact-text {
    color: #4a3a32;
    font-size: 15px;
    line-height: 1.55;
    margin-bottom: 12px;
}

.contact-link a {
    color: #8a2a22 !important;
    font-weight: 700;
    text-decoration: none;
}

.contact-link a:hover {
    text-decoration: underline;
}
/* Publications — sober style */

.publications-section {
    max-width: 980px;
    margin: 0 auto;
    padding: 34px 28px 20px 28px;
    color: #4a3a32;
}

.publications-section h2 {
    color: #8a2a22 !important;
    font-weight: 700 !important;
    font-size: 30px;
    margin-top: 8px;
    margin-bottom: 18px;
}

.publication-list {
    display: flex;
    flex-direction: column;
    gap: 22px;
    margin-top: 32px;
}

.publication-item {
    background: transparent !important;
    border-left: 2px solid rgba(138, 42, 34, 0.22);
    padding: 4px 0 4px 18px;
}

.publication-title {
    color: #5a2d27;
    font-weight: 650;
    font-size: 17px;
    line-height: 1.45;
    margin-bottom: 6px;
}

.publication-meta {
    color: #5a4a42;
    font-size: 14px;
    font-weight: 400;
    line-height: 1.55;
    margin-bottom: 8px;
}

.publication-text {
    color: #6a574e;
    font-size: 14px;
    line-height: 1.5;
    margin-bottom: 8px;
}

.publication-link {
    margin-top: 6px;
}

.publication-link a {
    color: #8a2a22 !important;
    font-size: 14px;
    font-weight: 600;
    text-decoration: none;
}

.publication-link a:hover {
    text-decoration: underline;
}

.bibtex-box {
    margin-top: 8px;
    background: transparent !important;
    border-left: none !important;
    padding: 0;
}

.bibtex-box summary {
    cursor: pointer;
    color: #9a6a45;
    font-size: 13px;
    font-weight: 600;
    margin-top: 6px;
}

.bibtex-box pre {
    white-space: pre-wrap;
    color: #4a3a32;
    font-size: 12px;
    line-height: 1.45;
    background: #fbf8f3;
    border: 1px solid rgba(138, 42, 34, 0.10);
    border-radius: 10px;
    padding: 12px;
    margin: 10px 0 0 0;
}

/* Repositories */

.repository-list {
    margin-top: 42px;
    padding-top: 26px;
}

.repository-title {
    color: #8a2a22;
    font-weight: 700;
    font-size: 22px;
    margin-bottom: 18px;
}

.repository-group-title {
    color: #9a6a45;
    font-weight: 700;
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 26px;
    margin-bottom: 10px;
}

.repository-item {
    border-left: 2px solid rgba(138, 42, 34, 0.20);
    padding: 4px 0 4px 18px;
    margin-bottom: 18px;
    color: #5a4a42;
    font-size: 14px;
    line-height: 1.55;
}

.repository-item strong {
    color: #5a2d27;
    font-size: 15px;
}

.repository-links {
    margin-top: 6px;
}

.repository-item a,
.repository-links a {
    color: #8a2a22 !important;
    font-size: 14px;
    font-weight: 600;
    text-decoration: none;
}

.repository-item a:hover,
.repository-links a:hover {
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

        with gr.Tab("Explore alignments"):
            default_corpus = "Lancelot"
            default_type = "Reviewed"

            segments = get_segment_choices(default_corpus, default_type)
            first_segment = segments[0] if segments else None
            witnesses = get_witness_choices(default_corpus, default_type)

            gr.Markdown(
                """
<div class="explore-section">

<div class="about-kicker">Browse · Compare · Inspect</div>

<h2>Explore alignments</h2>

<p class="about-lead">
Browse curated alignment samples produced with Aquilign and manually reviewed
for demonstration purposes. You can search across witnesses, choose which witnesses
to display, and inspect raw Aquilign output for transparency.
</p>

</div>
                """
            )

            notice_output = gr.HTML(
                value=corpus_notice(default_corpus, default_type)
            )

            with gr.Row():
                corpus_selector = gr.Dropdown(
                    choices=list(DATASETS.keys()),
                    value=default_corpus,
                    label="Corpus",
                    interactive=True,
                )

                type_selector = gr.Dropdown(
                    choices=["Reviewed", "Raw"],
                    value=default_type,
                    label="Alignment type",
                    interactive=True,
                )

            with gr.Row():
                search_box = gr.Textbox(
                    label="Search in witnesses",
                    placeholder="Search a word or expression, then press Enter...",
                )

                clear_button = gr.Button("Clear search")

            search_status = gr.HTML(value="")

            witness_selector = gr.CheckboxGroup(
                choices=witnesses,
                value=witnesses,
                label="Witnesses to display",
                interactive=True,
            )

            with gr.Row():
                previous_button = gr.Button("Previous segment")
                next_button = gr.Button("Next segment")

            segment_selector = gr.Dropdown(
                choices=segments,
                value=first_segment,
                label="Aligned segment",
                interactive=True,
            )

            parallel_output = gr.HTML(
                value=view_segment(default_corpus, default_type, first_segment, witnesses)
                if first_segment else "<p>No data found.</p>"
            )

            with gr.Row():
                download_button = gr.DownloadButton(
                    label="Download current dataset",
                    value=str(get_data_file(default_corpus, default_type)),
                )

            with gr.Accordion("Report an alignment issue", open=False):
                issue_text = gr.Textbox(
                    label="Issue report template",
                    value=make_issue_report(default_corpus, default_type, first_segment)
                    if first_segment else "",
                    lines=7,
                    interactive=True,
                )

                issue_link = gr.HTML(
                    value=make_github_issue_link(default_corpus, default_type, first_segment)
                    if first_segment else ""
                )

            with gr.Accordion("Full alignment table", open=False):
                table = gr.Dataframe(
                    value=load_alignments(default_corpus, default_type),
                    interactive=False,
                )

            corpus_selector.change(
                fn=update_explore,
                inputs=[corpus_selector, type_selector],
                outputs=[
                    segment_selector,
                    search_box,
                    witness_selector,
                    parallel_output,
                    table,
                    notice_output,
                    download_button,
                    issue_text,
                    issue_link,
                ],
            )

            type_selector.change(
                fn=update_explore,
                inputs=[corpus_selector, type_selector],
                outputs=[
                    segment_selector,
                    search_box,
                    witness_selector,
                    parallel_output,
                    table,
                    notice_output,
                    download_button,
                    issue_text,
                    issue_link,
                ],
            )

            search_box.submit(
                fn=update_search,
                inputs=[corpus_selector, type_selector, search_box, witness_selector],
                outputs=[
                    segment_selector,
                    parallel_output,
                    search_status,
                    issue_text,
                    issue_link,
                ],
            )

            clear_button.click(
                fn=clear_search,
                inputs=[corpus_selector, type_selector, witness_selector],
                outputs=[
                    search_box,
                    segment_selector,
                    parallel_output,
                    search_status,
                    issue_text,
                    issue_link,
                ],
            )

            previous_button.click(
                fn=lambda corpus, atype, segment, query, witnesses: move_segment(
                    corpus, atype, segment, query, witnesses, "previous"
                ),
                inputs=[
                    corpus_selector,
                    type_selector,
                    segment_selector,
                    search_box,
                    witness_selector,
                ],
                outputs=[
                    segment_selector,
                    parallel_output,
                    issue_text,
                    issue_link,
                ],
            )

            next_button.click(
                fn=lambda corpus, atype, segment, query, witnesses: move_segment(
                    corpus, atype, segment, query, witnesses, "next"
                ),
                inputs=[
                    corpus_selector,
                    type_selector,
                    segment_selector,
                    search_box,
                    witness_selector,
                ],
                outputs=[
                    segment_selector,
                    parallel_output,
                    issue_text,
                    issue_link,
                ],
            )

            segment_selector.change(
                fn=view_segment,
                inputs=[
                    corpus_selector,
                    type_selector,
                    segment_selector,
                    witness_selector,
                ],
                outputs=parallel_output,
            )

            segment_selector.change(
                fn=make_issue_report,
                inputs=[corpus_selector, type_selector, segment_selector],
                outputs=issue_text,
            )

            segment_selector.change(
                fn=make_github_issue_link,
                inputs=[corpus_selector, type_selector, segment_selector],
                outputs=issue_link,
            )

            witness_selector.change(
                fn=view_segment,
                inputs=[
                    corpus_selector,
                    type_selector,
                    segment_selector,
                    witness_selector,
                ],
                outputs=parallel_output,
            )

    

        with gr.Tab("About"):
            gr.Markdown(
                """
<div class="about-section">

<div class="about-kicker">Digital philology · Medieval texts · Multilingual alignment</div>

<h2>About Aquilign</h2>



<div class="about-question">
How can we align multilingual medieval textual traditions while preserving
their variation, transmission history, and philological complexity?
</div>

<p>
Aquilign is a multilingual alignment and collation engine
for historical and philological corpora.
It is designed to help researchers compare medieval textual traditions across
languages, witnesses, translations, and corpora.
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
Texts are divided into phrase-level units or clauses,
so that corresponding passages can be compared across witnesses and languages.
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
<div class="step-title">Review and curate</div>
<div class="step-text">
Automatic alignments may be inspected and corrected by researchers before
being presented as reviewed scholarly data.
</div>
</div>
</div>

<div class="method-step">
<div class="step-number">6</div>
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
The current demo presents reviewed alignment samples alongside raw Aquilign output
for transparency.
</p>

</div>
                """
            )
        with gr.Tab("Publications"):
            gr.Markdown(
                """
<div class="publications-section">

<div class="about-kicker">Publications · Citation · Datasets</div>

<h2>Publications</h2>

<p class="about-lead">
Please cite the relevant publications and datasets when using Aquilign,
the demo alignments, or the associated segmentation resources.
</p>

<div class="publication-list">

<div class="publication-item">
<div class="publication-title">
Textual Transmission without Borders: Multiple Multilingual Alignment and Stemmatology of the <em>Lancelot en prose</em> (Medieval French, Castilian, Italian)
</div>
<div class="publication-meta">
Gille Levenson, M., Ing, L., & Camps, J.-B. (2024). In <em>Proceedings of the Computational Humanities Research Conference 2024</em>, CEUR Workshop Proceedings, Vol. 3834, pp. 65–92.
</div>
<div class="publication-text">
Main publication presenting multilingual alignment and stemmatological analysis of the <em>Lancelot en prose</em> textual tradition.
</div>
<div class="publication-link">
<a href="https://ceur-ws.org/Vol-3834/#paper104" target="_blank">Paper</a>
</div>

<details class="bibtex-box">
<summary>BibTeX</summary>
<pre>
@inproceedings{gillelevenson_TextualTransmissionBorders_2024a,
  title = {Textual Transmission without Borders: Multiple Multilingual Alignment and Stemmatology of the ``Lancelot En Prose'' (Medieval French, Castilian, Italian)},
  shorttitle = {Textual Transmission without Borders},
  booktitle = {Proceedings of the Computational Humanities Research Conference 2024},
  author = {Gille Levenson, Matthias and Ing, Lucence and Camps, Jean-Baptiste},
  editor = {Haverals, Wouter and Koolen, Marijn and Thompson, Laure},
  date = {2024},
  series = {CEUR Workshop Proceedings},
  volume = {3834},
  pages = {65--92},
  publisher = {CEUR},
  location = {Aarhus, Denmark},
  issn = {1613-0073},
  url = {https://ceur-ws.org/Vol-3834/#paper104},
  urldate = {2024-12-09},
  eventtitle = {Computational Humanities Research 2024},
  langid = {english}
}
</pre>
</details>
</div>

<div class="publication-item">
<div class="publication-title">
Phrase-Level Segmentation on Medieval Corpora for Aligning Multilingual Texts
</div>
<div class="publication-meta">
Ing, L., Gille Levenson, M., & Macedo, C. (2026). In <em>Proceedings of the Fifteenth Language Resources and Evaluation Conference (LREC 2026)</em>.
</div>
<div class="publication-text">
Publication describing the phrase-level segmentation workflow and dataset used for aligning multilingual medieval corpora.
</div>
<div class="publication-link">
<a href="https://doi.org/10.63317/32HUZUUOKPFR" target="_blank">Paper</a>
</div>

<details class="bibtex-box">
<summary>BibTeX</summary>
<pre>
@inproceedings{ing2026phrase,
  title     = {Phrase-Level Segmentation on Medieval Corpora for Aligning Multilingual Texts},
  author    = {Ing, Lucence and Gille Levenson, Matthias and Macedo, Carolina},
  booktitle = {Proceedings of the Fifteenth Language Resources and Evaluation Conference (LREC 2026)},
  year      = {2026},
  doi       = {10.63317/32HUZUUOKPFR}
}
</pre>
</details>
</div>

</div>

<div class="repository-list">

<div class="repository-title">Resources and repositories</div>

<div class="repository-group-title">Tool</div>

<div class="repository-item">
<strong>Aquilign</strong><br>
Main multilingual alignment and collation tool.<br>
<div class="repository-links">
<a href="https://github.com/ProMeText/Aquilign" target="_blank">Aquilign repository</a>
</div>
</div>

<div class="repository-group-title">Demo corpora</div>

<div class="repository-item">
<strong>Lancelot par maints langages</strong><br>
Demo corpus for the <em>Lancelot en prose</em> tradition.<br>
<div class="repository-links">
<a href="https://github.com/ProMeText/lancelot-par-maints-langages" target="_blank">Lancelot repository</a>
</div>
</div>

<div class="repository-item">
<strong>Multilingual Aegidius</strong><br>
Demo corpus for <em>De regimine principum</em> and its multilingual transmission.<br>
<div class="repository-links">
<a href="https://github.com/ProMeText/Multilingual_Aegidius" target="_blank">Multilingual Aegidius repository</a>
</div>
</div>

<div class="repository-group-title">Datasets</div>

<div class="repository-item">
<strong>Multilingual Segmentation Dataset for Historical Prose</strong><br>
Dataset for phrase-level segmentation of historical prose, designed to support
the alignment of multilingual medieval textual traditions.<br>
<div class="repository-links">
<a href="https://github.com/ProMeText/multilingual-segmentation-dataset" target="_blank">Segmentation dataset repository</a><br>
<a href="https://doi.org/10.5281/zenodo.16992629" target="_blank">Zenodo DOI / archived dataset</a>
</div>
</div>

<div class="repository-item">
<strong>Parallel Corpus for Fine-Tuning LaBSE</strong><br>
Parallel multilingual corpus used to fine-tune LaBSE for sentence- and phrase-level
alignment of historical texts.<br>
<div class="repository-links">
<a href="https://github.com/ProMeText/parallelium-scriptures-alignment-dataset/tree/main" target="_blank">Fine-tuning corpus repository</a>
</div>
</div>

</div>

<p class="about-note">
These references document the alignment approach, segmentation workflow,
datasets, and corpus resources associated with Aquilign.
</p>

</div>
                """
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
        
<div class="contact-section">

<div class="about-kicker">Contact · Feedback · Collaboration</div>

<h2>Contact</h2>

<p class="about-lead">
For questions, feedback, or collaboration requests related to Aquilign,
you can contact the project team or open an issue on GitHub.
</p>

<div class="contact-grid">

<div class="contact-card">
<div class="contact-title">GitHub repository</div>
<div class="contact-text">
Use GitHub to report bugs, suggest improvements, or discuss alignment issues.
</div>
<div class="contact-link">
<a href="https://github.com/ProMeText/Aquilign" target="_blank">ProMeText/Aquilign</a>
</div>
</div>

<div class="contact-card">
<div class="contact-title">Report an alignment issue</div>
<div class="contact-text">
When reporting an issue, please include the corpus, alignment type, segment ID,
and a short description of the problem.
</div>
<div class="contact-link">
<a href="https://github.com/ProMeText/Aquilign/issues" target="_blank">Open GitHub issues</a>
</div>
</div>

<div class="contact-card">
<div class="contact-title">Collaboration and reuse</div>
<div class="contact-text">
For academic questions, reuse, or collaboration requests, please open a GitHub issue
with the relevant context. The team will follow up from there.
</div>
<div class="contact-link">
<a href="https://github.com/ProMeText/Aquilign/issues" target="_blank">Contact via GitHub</a>
</div>
</div>

</div>

<p class="about-note">
Aquilign is developed as an open-source research tool for digital philology,
historical linguistics, and computational humanities.
</p>

</div>
                """
        )


demo.launch(allowed_paths=["team", "sample_data"])
