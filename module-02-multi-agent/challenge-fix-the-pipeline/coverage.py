"""Coverage check for the research pipeline.

The corpus covers four segments of the creative industries. A complete report
should say something about each one. This module checks a finished report for
signs of each segment and prints a checklist, so you can tell at a glance
whether the pipeline covered the whole question or only part of it.

It is a keyword check, not a judge of quality. It tells you whether a segment
was addressed at all.
"""

# Each segment lists words that only show up when that segment is discussed.
SEGMENTS = {
    "visual arts": ["illustrat", "gallery", "galleries", "curat"],
    "music": ["music", "session player", "session musician", "catalog", "royalt"],
    "writing": ["writing", "writer", "copy rates", "publisher", "manuscript"],
    "film production": ["film", "vfx", "visual effects", "performer", "likeness"],
}


def check_coverage(report_text):
    """Return a dict of segment name -> True if the report mentions it."""
    lowered = report_text.lower()
    found = {}
    for segment in SEGMENTS:
        keywords = SEGMENTS[segment]
        hit = False
        for word in keywords:
            if word in lowered:
                hit = True
        found[segment] = hit
    return found


def print_coverage(report_text):
    """Print the coverage checklist and say whether the run passed."""
    found = check_coverage(report_text)
    print("\nCoverage check")
    print("-" * 30)
    covered = 0
    for segment in found:
        if found[segment]:
            print(f"  COVERED  {segment}")
            covered = covered + 1
        else:
            print(f"  MISSING  {segment}")
    print("-" * 30)
    print(f"{covered} of {len(found)} segments covered")
    if covered == len(found):
        print("Complete coverage. The pipeline answered the whole question.")
    else:
        print("Incomplete. Some segments of the question went unanswered.")
    return covered == len(found)
