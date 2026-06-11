from citeproc_endnote_uv.docx_reference_list_to_ris import author_list, parse_reference, write_record
from citeproc_endnote_uv.docx_numeric_to_endnote_temp import Reference, make_temp_citation


def test_author_list_preserves_all_named_authors():
    authors = (
        "Ferrari, Karin J., Scelfo, A., Jammula, S., Cuomo, A., Barozzi, I., "
        "Stutzer, A., Fischle, W., Bonaldi, T., and Pasini, D."
    )

    assert author_list(authors) == [
        "Ferrari, Karin J.",
        "Scelfo, A.",
        "Jammula, S.",
        "Cuomo, A.",
        "Barozzi, I.",
        "Stutzer, A.",
        "Fischle, W.",
        "Bonaldi, T.",
        "Pasini, D.",
    ]


def test_reference_record_writes_all_authors():
    reference = parse_reference(
        28,
        "Ferrari, Karin J., Scelfo, A., Jammula, S., Cuomo, A., Barozzi, I., "
        "Stutzer, A., Fischle, W., Bonaldi, T., and Pasini, D. (2014). "
        "Polycomb-Dependent H3K27me1 and H3K27me2 Regulate Active Transcription and Enhancer Fidelity. "
        "Molecular Cell 53, 49-62. 10.1016/j.molcel.2013.10.030.",
    )

    assert reference is not None
    record = "\n".join(write_record(reference))
    assert "AU  - Ferrari, Karin J." in record
    assert "AU  - Scelfo, A." in record
    assert "AU  - Pasini, D." in record
    assert "DO  - 10.1016/j.molcel.2013.10.030" in record


def test_only_true_author_year_collisions_need_titles():
    references = {
        1: Reference("McCabe", "2012", "Mutation of A677 in histone methyltransferase EZH2"),
        2: Reference("McCabe", "2012", "EZH2 inhibition as a therapeutic strategy"),
        3: Reference("Lee", "2015", "Genome-wide activities of Polycomb complexes"),
        4: Reference("Lee", "2015", "Genome-wide activities of Polycomb complexes"),
    }
    ambiguous_keys = {"McCabe, 2012"}

    assert make_temp_citation("1,2", references, ambiguous_keys) == (
        "{McCabe, 2012, Mutation of A677 in histone methyltransferase EZH2; "
        "McCabe, 2012, EZH2 inhibition as a therapeutic strategy}"
    )
    assert make_temp_citation("3", references, ambiguous_keys) == "{Lee, 2015}"
