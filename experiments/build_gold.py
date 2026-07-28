#!/usr/bin/env python3
"""Create and validate the complete, paper-trail gold mapping."""

from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


@dataclass(frozen=True)
class Gold:
    targets: tuple[tuple[str, str], ...]
    difficulty: str
    rationale: str


GOLD: dict[str, Gold] = {
    # ContractAward
    "contract_award_unique_key": Gold(
        (("Award", "id"),),
        "hard",
        "The USAspending key identifies the prime award; OCDS Award.id is the "
        "identifier scoped to an award.",
    ),
    "prime_award_base_transaction_description": Gold(
        (("Award", "description"), ("Contract", "description")),
        "context",
        "The same plain-language procurement description is applicable to the "
        "OCDS award and resulting contract descriptions.",
    ),
    "action_date": Gold(
        (("Award", "date"), ("Contract", "dateSigned")),
        "context",
        "USAspending defines the action date as issue/signature or binding "
        "agreement date, spanning both OCDS award and contract-signing dates.",
    ),
    "award_latest_action_date": Gold(
        (("Release", "date"),),
        "hard",
        "The latest recorded award action is the closest source timestamp for "
        "the corresponding OCDS release event.",
    ),
    "period_of_performance_start_date": Gold(
        (("Award", "contractPeriod.startDate"), ("Contract", "period.startDate")),
        "easy",
        "Both target paths represent the start of contract performance.",
    ),
    "period_of_performance_current_end_date": Gold(
        (("Award", "contractPeriod.endDate"), ("Contract", "period.endDate")),
        "easy",
        "Both target paths represent the scheduled current end of performance.",
    ),
    "period_of_performance_potential_end_date": Gold(
        (
            ("Award", "contractPeriod.maxExtentDate"),
            ("Contract", "period.maxExtentDate"),
        ),
        "datatype",
        "The potential end date, including options, matches the maximum extent "
        "date rather than the current end date.",
    ),
    "current_total_value_of_award": Gold(
        (("Award", "value.amount"), ("Contract", "value.amount")),
        "context",
        "The obligated value to date can populate the value of the award and "
        "the associated contract in the selected publication profile.",
    ),
    "potential_total_value_of_award": Gold(
        (("Tender", "value.amount"),),
        "hard",
        "The total possible value including options is closest to the tender's "
        "upper estimated procurement value.",
    ),
    "total_obligated_amount": Gold(
        (("Award", "value.amount"),),
        "context",
        "The cumulative obligated amount is the selected award value measure.",
    ),
    "total_outlayed_amount_for_overall_award": Gold(
        (),
        "no_match",
        "The fixed target excludes OCDS implementation transactions, and no "
        "selected target property represents cumulative government outlays.",
    ),
    "solicitation_identifier": Gold(
        (("Tender", "id"),),
        "easy",
        "Both fields identify the solicitation/tender within the contracting process.",
    ),
    "solicitation_date": Gold(
        (("Tender", "tenderPeriod.startDate"),),
        "context",
        "Solicitation issuance begins the target tender period.",
    ),
    "parent_award_id_piid": Gold(
        (("Contract", "relatedProcesses.identifier"),),
        "hard",
        "The referenced parent award identifier is represented as an identifier "
        "of a related contracting process.",
    ),
    # AwardingOrganization
    "awarding_agency_code": Gold(
        (("Tender", "procuringEntity.id"), ("Organization", "identifier.id")),
        "abbreviation",
        "The agency code identifies both the tender's procuring entity reference "
        "and the corresponding organization identifier.",
    ),
    "awarding_agency_name": Gold(
        (("Tender", "procuringEntity.name"), ("Organization", "name")),
        "easy",
        "The awarding agency is the procuring entity and an organization.",
    ),
    "awarding_sub_agency_code": Gold(
        (("Organization", "identifier.id"),),
        "abbreviation",
        "The sub-tier agency code is an organization identifier.",
    ),
    "awarding_sub_agency_name": Gold(
        (("Organization", "name"),),
        "easy",
        "The sub-tier agency name is an organization name.",
    ),
    "awarding_office_code": Gold(
        (("Organization", "identifier.id"),),
        "abbreviation",
        "The awarding office code identifies an organization in the federal hierarchy.",
    ),
    "awarding_office_name": Gold(
        (("Organization", "name"),),
        "easy",
        "The awarding office name is an organization name.",
    ),
    "funding_agency_code": Gold(
        (("Organization", "identifier.id"),),
        "context",
        "The funding agency is modeled as an organization identified by this code.",
    ),
    "funding_agency_name": Gold(
        (("Organization", "name"),),
        "context",
        "The funding agency is modeled as an organization with this name.",
    ),
    # RecipientOrganization
    "recipient_uei": Gold(
        (("Organization", "identifier.id"), ("Award", "suppliers.id")),
        "abbreviation",
        "UEI is the recipient's legal-entity identifier and supplier reference ID.",
    ),
    "recipient_name": Gold(
        (("Organization", "name"), ("Award", "suppliers.name")),
        "easy",
        "The recipient legal name is the organization and supplier name.",
    ),
    "recipient_doing_business_as_name": Gold(
        (),
        "no_match",
        "OCDS 1.1.5 core has no dedicated doing-business-as organization property.",
    ),
    "recipient_parent_uei": Gold(
        (),
        "no_match",
        "The fixed OCDS subset has no parent-organization relationship for a "
        "recipient's ultimate parent UEI.",
    ),
    "recipient_parent_name": Gold(
        (),
        "no_match",
        "The fixed OCDS subset has no parent-organization relationship for a "
        "recipient's ultimate parent name.",
    ),
    "cage_code": Gold(
        (("Organization", "identifier.id"),),
        "abbreviation",
        "CAGE is an organization identifier; its scheme is external context, "
        "not encoded in this source column.",
    ),
    "contracting_officers_determination_of_business_size_code": Gold(
        (),
        "no_match",
        "OCDS core Organization.details is unstructured and the fixed target has "
        "no named business-size determination property.",
    ),
    "veteran_owned_business": Gold(
        (),
        "no_match",
        "The fixed target has no named veteran-owned-business characteristic.",
    ),
    "woman_owned_business": Gold(
        (),
        "no_match",
        "The fixed target has no named woman-owned-business characteristic.",
    ),
    "service_disabled_veteran_owned_business": Gold(
        (),
        "no_match",
        "The fixed target has no named service-disabled-veteran-owned characteristic.",
    ),
    # PlaceOfPerformance
    "primary_place_of_performance_city_name": Gold(
        (("Address", "locality"), ("Organization", "address.locality")),
        "easy",
        "A city name is the locality component of an address.",
    ),
    "primary_place_of_performance_county_name": Gold(
        (),
        "no_match",
        "The selected OCDS Address has no county property.",
    ),
    "primary_place_of_performance_state_code": Gold(
        (("Address", "region"), ("Organization", "address.region")),
        "datatype",
        "The state code is a coded representation of the address region.",
    ),
    "primary_place_of_performance_state_name": Gold(
        (("Address", "region"), ("Organization", "address.region")),
        "easy",
        "The state name is the address region.",
    ),
    "primary_place_of_performance_country_code": Gold(
        (),
        "no_match",
        "The selected OCDS Address contains countryName but no country-code property.",
    ),
    "primary_place_of_performance_country_name": Gold(
        (("Address", "countryName"), ("Organization", "address.countryName")),
        "easy",
        "The country name is the address countryName.",
    ),
    "primary_place_of_performance_zip_4": Gold(
        (("Address", "postalCode"), ("Organization", "address.postalCode")),
        "datatype",
        "ZIP+4 is a postal code value.",
    ),
    "primary_place_of_performance_congressional_district": Gold(
        (),
        "no_match",
        "The selected OCDS Address has no congressional-district property.",
    ),
    # ProcurementClassification
    "product_or_service_code": Gold(
        (
            ("Classification", "id"),
            ("Item", "classification.id"),
            ("Award", "items.classification.id"),
        ),
        "abbreviation",
        "PSC is a classification identifier at reusable, item, and awarded-item levels.",
    ),
    "product_or_service_code_description": Gold(
        (
            ("Classification", "description"),
            ("Item", "classification.description"),
            ("Award", "items.classification.description"),
        ),
        "easy",
        "The PSC label is a classification description at the three selected levels.",
    ),
    "naics_code": Gold(
        (
            ("Classification", "id"),
            ("Item", "classification.id"),
            ("Award", "items.classification.id"),
        ),
        "abbreviation",
        "NAICS is an industry classification identifier.",
    ),
    "naics_description": Gold(
        (
            ("Classification", "description"),
            ("Item", "classification.description"),
            ("Award", "items.classification.description"),
        ),
        "easy",
        "The NAICS label is a classification description.",
    ),
    "extent_competed_code": Gold(
        (("Tender", "procurementMethodDetails"),),
        "hard",
        "The FPDS competition code supplies publisher-specific detail about the "
        "procurement method.",
    ),
    "solicitation_procedures_code": Gold(
        (("Tender", "procurementMethodDetails"),),
        "hard",
        "The coded solicitation procedure is publisher-specific procurement-method detail.",
    ),
    "type_of_set_aside_code": Gold(
        (("Tender", "procurementMethodRationale"),),
        "context",
        "A set-aside code explains the policy rationale for restricting the procurement.",
    ),
    "type_of_contract_pricing_code": Gold(
        (),
        "no_match",
        "The fixed OCDS 1.1.5 target has no contract-pricing-arrangement property.",
    ),
    "domestic_or_foreign_entity_code": Gold(
        (),
        "no_match",
        "The fixed target has no named domestic/foreign ownership classification.",
    ),
    "country_of_product_or_service_origin_code": Gold(
        (),
        "no_match",
        "The fixed target has no item country-of-origin property.",
    ),
    "dod_acquisition_program_code": Gold(
        (("Classification", "id"),),
        "abbreviation",
        "The DoD acquisition program code is a domain-specific classification identifier.",
    ),
    "dod_claimant_program_code": Gold(
        (("Classification", "id"),),
        "abbreviation",
        "The DoD claimant program code is a classification identifier.",
    ),
    "contingency_humanitarian_or_peacekeeping_operation_code": Gold(
        (),
        "no_match",
        "The fixed target has no named contingency/humanitarian-operation code property.",
    ),
    "sea_transportation_code": Gold(
        (),
        "no_match",
        "The fixed target has no property for anticipated sea transport of supplies.",
    ),
    "subcontracting_plan_code": Gold(
        (),
        "no_match",
        "The fixed target does not encode FPDS subcontracting-plan requirement codes.",
    ),
}


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    source_path = DATA / "source_schema.csv"
    target_path = DATA / "target_ontology.csv"
    source_rows = load_csv(source_path)
    target_rows = load_csv(target_path)
    sources = {(row["TableName"], row["ColumnName"]) for row in source_rows}
    source_by_column = {row["ColumnName"]: row for row in source_rows}
    if len(source_by_column) != len(source_rows):
        raise ValueError("source column names must be unique in this fixed subset")
    if set(source_by_column) != set(GOLD):
        missing = sorted(set(source_by_column) - set(GOLD))
        extra = sorted(set(GOLD) - set(source_by_column))
        raise ValueError(f"gold coverage mismatch; missing={missing}, extra={extra}")
    targets = {(row["ObjectType"], row["PropertyName"]) for row in target_rows}

    output: list[dict[str, str]] = []
    for source_table, source_column in sorted(sources):
        annotation = GOLD[source_column]
        mapping_type = (
            "no-match"
            if not annotation.targets
            else "1:1"
            if len(annotation.targets) == 1
            else "1:n"
        )
        pairs = annotation.targets or (("", ""),)
        for target_object_type, target_property in pairs:
            if (
                target_object_type
                and (target_object_type, target_property) not in targets
            ):
                raise ValueError(
                    f"unknown target: {target_object_type}.{target_property}"
                )
            target_location = (
                f"OCDS 1.1.5 canonical schema: {target_object_type}.{target_property}"
                if target_object_type
                else "OCDS 1.1.5 fixed 108-property subset reviewed; no equivalent"
            )
            output.append(
                {
                    "source_table": source_table,
                    "source_column": source_column,
                    "target_object_type": target_object_type,
                    "target_property": target_property,
                    "mapping_type": mapping_type,
                    "difficulty": annotation.difficulty,
                    "rationale": annotation.rationale,
                    "evidence_source": "USAspending data dictionary; OCDS 1.1.5 schema",
                    "evidence_location": (
                        f"USAspending field {source_column}; {target_location}"
                    ),
                    "annotation_status": "draft_complete",
                    "review_status": "deterministically_validated_not_independent",
                }
            )

    output_path = DATA / "gold_mapping.csv"
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(output[0]))
        writer.writeheader()
        writer.writerows(output)

    no_match = sum(not annotation.targets for annotation in GOLD.values())
    one_to_many = sum(len(annotation.targets) > 1 for annotation in GOLD.values())
    manifest_path = DATA / "schema_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest.update(
        {
            "gold_source_coverage": len(GOLD),
            "gold_pairs_or_no_match_rows": len(output),
            "gold_no_match_sources": no_match,
            "gold_one_to_many_sources": one_to_many,
            "gold_mapping_sha256": sha256(output_path),
            "annotation_status": "draft_complete",
            "review_status": "deterministically_validated_not_independent",
        }
    )
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
