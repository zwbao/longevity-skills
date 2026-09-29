"""Array calls, clinical diplotypes and CPIC rows, all on synthetic genotypes.

Expected phenotypes and categories come from CPIC's own tables in
data/cpic_tables.json and the guideline sentences quoted in each test.
"""

import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_cpic_tables import category_for  # noqa: E402
from cpic_calls import (  # noqa: E402
    call_from_array,
    drug_result,
    format_activity,
    load_tables,
    parse_diplotype_lines,
)
from genotype_file import GenotypeFile  # noqa: E402
from presets import ARRAY_PANEL  # noqa: E402

TABLES = load_tables()


def array(gene, **calls):
    genotypes = GenotypeFile(calls={rsid.lower(): value for rsid, value in calls.items()}, rows=len(calls))
    return call_from_array(TABLES, gene, genotypes, ARRAY_PANEL[gene]["reference_label"])


def only(call):
    assert call.called, (call.diplotypes, call.phenotypes)
    return call.phenotypes[0]


# --- strand ---------------------------------------------------------------


def test_panel_bases_are_on_the_genomic_plus_strand():
    """CPIC allele values equal the ref/alt of the GRCh38 g. HGVS, as consumer files report."""
    for gene, panel in TABLES["genes"].items():
        for site in panel["sites"]:
            changes = re.findall(r"g\.\d+([ACGT])>([ACGT])", site["grch38"])
            assert changes, site
            refs = {ref for ref, _alt in changes}
            alts = {alt for _ref, alt in changes}
            assert site["reference_base"] in refs, (gene, site)
            for name, allele in panel["alleles"].items():
                value = allele["at_sites"][site["rsid"]]
                if value != site["reference_base"] and len(value) == 1 and value in "ACGT":
                    assert value in alts, (gene, name, site)


def test_minus_strand_genes_use_plus_strand_letters():
    # TPMT and VKORC1 are on the minus strand; CPIC stores the plus-strand base.
    tpmt = TABLES["genes"]["TPMT"]
    assert tpmt["alleles"]["*2"]["at_sites"]["rs1800462"] == "G"  # c.238G>C on the gene
    assert tpmt["alleles"]["*3B"]["at_sites"]["rs1800460"] == "T"  # c.460G>A on the gene
    assert TABLES["warfarin_sites"]["VKORC1"]["grch38"].endswith("C>T")  # -1639G>A on the gene


# --- array calls ------------------------------------------------------------


def test_cyp2c19_star2_heterozygote_is_intermediate():
    call = array("CYP2C19", rs4244285="AG", rs4986893="GG", rs28399504="AA", rs12248560="CC")
    assert call.diplotypes == ["*1/*2"]
    assert only(call) == "Intermediate Metabolizer"


def test_cyp2c19_star2_star3_is_poor():
    call = array("CYP2C19", rs4244285="AG", rs4986893="AG", rs28399504="AA", rs12248560="CC")
    assert only(call) == "Poor Metabolizer"


def test_cyp2c19_star17():
    assert only(array("CYP2C19", rs4244285="GG", rs12248560="CT")) == "Rapid Metabolizer"
    assert only(array("CYP2C19", rs4244285="GG", rs12248560="TT")) == "Ultrarapid Metabolizer"


def test_cyp2c19_star2_with_star17_is_intermediate():
    # CPIC lookup: one no-function plus one increased-function allele -> Intermediate Metabolizer.
    assert only(array("CYP2C19", rs4244285="AG", rs12248560="CT")) == "Intermediate Metabolizer"


def test_cyp2c19_star4_carries_either_base_at_star17_site():
    # *4 is defined with Y (C or T) at rs12248560, so *4 + T is *4 on one strand or *4/*17.
    call = array("CYP2C19", rs4244285="GG", rs28399504="AG", rs12248560="CT")
    assert only(call) == "Intermediate Metabolizer"
    assert len(call.diplotypes) >= 1


def test_tpmt_double_heterozygote_is_not_called():
    call = array("TPMT", rs1800462="CC", rs1800460="CT", rs1142345="TC")
    assert not call.called
    assert set(call.phenotypes) == {"Intermediate Metabolizer", "Poor Metabolizer"}
    assert "*1/*3A" in call.diplotypes and "*3B/*3C" in call.diplotypes


def test_tpmt_single_variant():
    assert only(array("TPMT", rs1800462="CC", rs1800460="CC", rs1142345="TC")) == "Intermediate Metabolizer"
    assert only(array("TPMT", rs1800462="CC", rs1800460="TT", rs1142345="CC")) == "Poor Metabolizer"


def test_cyp2c9_activity_scores():
    call = array("CYP2C9", rs1799853="CC", rs1057910="AC")
    assert only(call) == "Intermediate Metabolizer" and call.lookup_values == ["1.0"]
    call = array("CYP2C9", rs1799853="CT", rs1057910="AC")
    assert only(call) == "Poor Metabolizer" and call.lookup_values == ["0.5"]
    call = array("CYP2C9", rs1799853="CT", rs1057910="AA")
    assert call.lookup_values == ["1.5"]


def test_dpyd_c2846_heterozygote():
    call = array("DPYD", rs3918290="CC", rs55886062="AA", rs67376798="TA", rs75017182="GG", rs56038477="CC")
    assert only(call) == "Intermediate Metabolizer" and call.lookup_values == ["1.5"]


def test_nudt15_slco1b1_abcg2_cyp3a5():
    assert only(array("NUDT15", rs116855232="TT")) == "Poor Metabolizer"
    assert only(array("SLCO1B1", rs4149056="CC")) == "Poor Function"
    assert only(array("SLCO1B1", rs4149056="TC")) == "Decreased Function"
    assert only(array("ABCG2", rs2231142="TT")) == "Poor Function"
    assert only(array("CYP3A5", rs776746="CC", rs10264272="CC")) == "Poor Metabolizer"
    assert only(array("CYP3A5", rs776746="TC", rs10264272="CC")) == "Intermediate Metabolizer"


def test_complement_strand_letters_are_not_used():
    call = array("CYP2C19", rs4244285="CT")  # complement of G/A
    assert call.source == "unreadable"
    assert call.unusable and call.unusable[0][0] == "rs4244285"


def test_indel_letters_and_missing_sites():
    call = array("CYP3A5", rs776746="DI")
    assert call.source == "unreadable"
    call = array("CYP2C9", rs1799853="CC")
    assert only(call) == "Normal Metabolizer"
    assert ("*3", ["rs1057910"]) in call.not_assessed


def test_no_panel_site_means_not_tested():
    assert array("CYP2C19").source == "not_tested"


# --- clinical diplotypes ----------------------------------------------------


@pytest.mark.parametrize("line, phenotype, score", [
    ("CYP2D6 *1/*10", "Normal Metabolizer", "1.25"),
    ("CYP2D6 *10/*10", "Intermediate Metabolizer", "0.5"),
    ("CYP2D6 *36+*10/*10", "Intermediate Metabolizer", "0.5"),
    ("CYP2D6 *1/*5", "Intermediate Metabolizer", "1.0"),
    ("CYP2D6 *4/*4", "Poor Metabolizer", "0.0"),
    ("CYP2D6 *1x2/*1", "Ultrarapid Metabolizer", "3.0"),
])
def test_cyp2d6_activity_score_from_clinical_result(line, phenotype, score):
    calls, problems = parse_diplotype_lines(TABLES, line)
    assert not problems
    assert calls["CYP2D6"].phenotypes == [phenotype]
    assert calls["CYP2D6"].lookup_values == [score]


def test_unknown_clinical_allele_is_indeterminate():
    calls, _ = parse_diplotype_lines(TABLES, "CYP2D6 *1/*9999")
    assert calls["CYP2D6"].phenotypes == ["Indeterminate"]


def test_unparsable_clinical_line_is_a_problem():
    _, problems = parse_diplotype_lines(TABLES, "我是慢代谢")
    assert problems


def test_format_activity():
    assert [format_activity(x) for x in (0, 0.25, 1, 1.5, 2.25)] == ["0.0", "0.25", "1.0", "1.5", "2.25"]


# --- CPIC rows --------------------------------------------------------------


def categories(drug, calls):
    result = drug_result(TABLES, drug, calls)
    return {branch.population: branch.categories for branch in result.branches}, result


def test_clopidogrel_follows_cpic_2022():
    """CPIC 2022, ACS/PCI: poor metabolizer 'Avoid clopidogrel if possible. Use prasugrel or
    ticagrelor at standard dose if no contraindication.' (Strong); normal metabolizer
    'If considering clopidogrel, use at standard dose'."""
    poor = {"CYP2C19": array("CYP2C19", rs4244285="AA")}
    found, result = categories("clopidogrel", poor)
    assert found["CVI ACS PCI"] == ["avoid"]
    assert [row["classification"] for row in next(b for b in result.branches if b.population == "CVI ACS PCI").rows] == ["Strong"]
    normal = {"CYP2C19": array("CYP2C19", rs4244285="GG", rs12248560="CC")}
    found, _ = categories("clopidogrel", normal)
    assert set(found) == {"CVI ACS PCI", "CVI non-ACS non-PCI", "NVI"}
    assert all(value == ["standard"] for value in found.values())


def test_simvastatin_poor_function_is_alternative():
    """CPIC 2022 statins, SLCO1B1 poor function: 'Prescribe an alternative statin depending on the desired potency'."""
    found, _ = categories("simvastatin", {"SLCO1B1": array("SLCO1B1", rs4149056="CC")})
    assert found == {"general": ["avoid"]}


def test_celecoxib_cyp2c9_poor_is_caution():
    """CPIC 2020 NSAIDs, activity score 0.5: 'Initiate therapy with 25-50% of the lowest recommended starting dose.'"""
    found, _ = categories("celecoxib", {"CYP2C9": array("CYP2C9", rs1799853="CT", rs1057910="AC")})
    assert found == {"general": ["caution"]}


def test_allopurinol_hla_b():
    """CPIC allopurinol: HLA-B*58:01 positive 'Allopurinol is contraindicated'."""
    calls, _ = parse_diplotype_lines(TABLES, "HLA-B*58:01 阳性")
    found, _ = categories("allopurinol", calls)
    assert found == {"general": ["avoid"]}
    calls, _ = parse_diplotype_lines(TABLES, "HLA-B*58:01 阴性")
    assert categories("allopurinol", calls)[0] == {"general": ["standard"]}


def test_hla_b_without_colon_as_on_chinese_reports():
    calls, problems = parse_diplotype_lines(TABLES, "HLA-B*5801 阳性")
    assert not problems
    assert categories("allopurinol", calls)[0] == {"general": ["avoid"]}


def test_ppi_direction_follows_cpic_2020():
    """CPIC PPIs: normal metabolizer 'Initiate standard starting daily dose. Consider increasing dose by 50-100%
    for the treatment of H. pylori...'; poor metabolizer 'Initiate standard starting daily dose. For chronic
    therapy (>12 weeks) and efficacy achieved, consider 50% reduction...'; ultrarapid 'Increase starting daily
    dose by 100%.'"""
    normal = {"CYP2C19": array("CYP2C19", rs4244285="GG", rs12248560="CC")}
    poor = {"CYP2C19": array("CYP2C19", rs4244285="AA")}
    ultra = {"CYP2C19": array("CYP2C19", rs4244285="GG", rs12248560="TT")}
    for drug in ("omeprazole", "lansoprazole", "pantoprazole", "dexlansoprazole"):
        assert categories(drug, normal)[0] == {"general": ["standard"]}
        assert categories(drug, poor)[0] == {"general": ["standard"]}
        assert categories(drug, ultra)[0] == {"general": ["caution"]}


def test_tacrolimus_direction_follows_cpic_2015():
    """CPIC tacrolimus: expressers 'Increase starting dose 1.5 to 2 times recommended starting dose';
    CYP3A5 poor metabolizers (*3/*3) 'Initiate therapy with standard recommended dose'."""
    assert categories("tacrolimus", {"CYP3A5": array("CYP3A5", rs776746="CC", rs10264272="CC")})[0] == {"general": ["standard"]}
    assert categories("tacrolimus", {"CYP3A5": array("CYP3A5", rs776746="TT", rs10264272="CC")})[0] == {"general": ["caution"]}


def test_hla_b_result_for_one_allele_is_no_result_for_another():
    calls, _ = parse_diplotype_lines(TABLES, "HLA-B*58:01 阴性")
    result = drug_result(TABLES, "carbamazepine", calls)
    assert result.status == "needs_test"


def test_cyp2d6_drugs_need_a_clinical_result():
    result = drug_result(TABLES, "codeine", {})
    assert result.status == "needs_test" and result.needs == ["CYP2D6"]


def test_tpmt_ambiguity_carries_both_categories():
    calls = {
        "TPMT": array("TPMT", rs1800462="CC", rs1800460="CT", rs1142345="TC"),
        "NUDT15": array("NUDT15", rs116855232="CC"),
    }
    found, _ = categories("azathioprine", calls)
    assert len(found["general"]) >= 2


def test_every_stored_category_follows_the_rule():
    for drug, entry in TABLES["drugs"].items():
        for row in entry["rows"]:
            assert row["category"] == category_for(row["recommendation"]), (drug, row["id"])


@pytest.mark.parametrize("text, expected", [
    ("Avoid clopidogrel if possible. Use prasugrel or ticagrelor at standard dose if no contraindication.", "avoid"),
    ("Avoid moderate and strong CYP2D6 inhibitors. Initiate therapy with recommended standard of care dosing (tamoxifen 20 mg/day).", "standard"),
    ("Initiate therapy with recommended starting dose. Consider a slower titration schedule and lower maintenance dose than normal metabolizers.", "caution"),
    ("Prescribe desired starting dose and adjust doses based on disease-specific guidelines.", "standard"),
    ("Reduce starting dose by 50% followed by titration of dose based on toxicity or therapeutic drug monitoring (if available).", "caution"),
    ("No recommendation", "none"),
])
def test_category_rule_examples(text, expected):
    assert category_for(text) == expected
