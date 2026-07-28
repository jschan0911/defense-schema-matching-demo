#!/usr/bin/env python3
"""Build fixed source and target metadata CSVs from official public metadata."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "data" / "public"
DATA = ROOT / "data"

SOURCE_FIELDS: dict[str, list[str]] = {
    "ContractAward": [
        "contract_award_unique_key",
        "prime_award_base_transaction_description",
        "action_date",
        "award_latest_action_date",
        "period_of_performance_start_date",
        "period_of_performance_current_end_date",
        "period_of_performance_potential_end_date",
        "current_total_value_of_award",
        "potential_total_value_of_award",
        "total_obligated_amount",
        "total_outlayed_amount_for_overall_award",
        "solicitation_identifier",
        "solicitation_date",
        "parent_award_id_piid",
    ],
    "AwardingOrganization": [
        "awarding_agency_code",
        "awarding_agency_name",
        "awarding_sub_agency_code",
        "awarding_sub_agency_name",
        "awarding_office_code",
        "awarding_office_name",
        "funding_agency_code",
        "funding_agency_name",
    ],
    "RecipientOrganization": [
        "recipient_uei",
        "recipient_name",
        "recipient_doing_business_as_name",
        "recipient_parent_uei",
        "recipient_parent_name",
        "cage_code",
        "contracting_officers_determination_of_business_size_code",
        "veteran_owned_business",
        "woman_owned_business",
        "service_disabled_veteran_owned_business",
    ],
    "PlaceOfPerformance": [
        "primary_place_of_performance_city_name",
        "primary_place_of_performance_county_name",
        "primary_place_of_performance_state_code",
        "primary_place_of_performance_state_name",
        "primary_place_of_performance_country_code",
        "primary_place_of_performance_country_name",
        "primary_place_of_performance_zip_4",
        "primary_place_of_performance_congressional_district",
    ],
    "ProcurementClassification": [
        "product_or_service_code",
        "product_or_service_code_description",
        "naics_code",
        "naics_description",
        "extent_competed_code",
        "solicitation_procedures_code",
        "type_of_set_aside_code",
        "type_of_contract_pricing_code",
        "domestic_or_foreign_entity_code",
        "country_of_product_or_service_origin_code",
        "dod_acquisition_program_code",
        "dod_claimant_program_code",
        "contingency_humanitarian_or_peacekeeping_operation_code",
        "sea_transportation_code",
        "subcontracting_plan_code",
    ],
}

TABLE_DESCRIPTIONS = {
    "ContractAward": (
        "Identifiers, descriptions, dates, periods, and monetary totals for a "
        "USAspending Department of Defense prime contract award."
    ),
    "AwardingOrganization": (
        "Awarding and funding federal organization identifiers and names."
    ),
    "RecipientOrganization": (
        "Public registration identifiers, names, and selected business "
        "characteristics of a contract recipient."
    ),
    "PlaceOfPerformance": (
        "Public geographic descriptors for the primary place where award "
        "performance occurs; no raw award locations are retained."
    ),
    "ProcurementClassification": (
        "Product, industry, competition, pricing, and selected DoD-specific "
        "procurement classification fields."
    ),
}

TARGET_PATHS: dict[str, list[str]] = {
    "Release": [
        "ocid",
        "id",
        "date",
        "tag",
        "initiationType",
        "language",
    ],
    "Tender": [
        "id",
        "title",
        "description",
        "status",
        "procuringEntity.id",
        "procuringEntity.name",
        "value.amount",
        "value.currency",
        "minValue.amount",
        "minValue.currency",
        "procurementMethod",
        "procurementMethodDetails",
        "procurementMethodRationale",
        "mainProcurementCategory",
        "additionalProcurementCategories",
        "awardCriteria",
        "awardCriteriaDetails",
        "submissionMethod",
        "submissionMethodDetails",
        "tenderPeriod.startDate",
        "tenderPeriod.endDate",
        "contractPeriod.startDate",
        "contractPeriod.endDate",
        "numberOfTenderers",
    ],
    "Award": [
        "id",
        "title",
        "description",
        "status",
        "date",
        "value.amount",
        "value.currency",
        "suppliers.id",
        "suppliers.name",
        "contractPeriod.startDate",
        "contractPeriod.endDate",
        "contractPeriod.maxExtentDate",
        "contractPeriod.durationInDays",
        "items.id",
        "items.description",
        "items.classification.scheme",
        "items.classification.id",
        "items.classification.description",
    ],
    "Contract": [
        "id",
        "awardID",
        "title",
        "description",
        "status",
        "period.startDate",
        "period.endDate",
        "period.maxExtentDate",
        "period.durationInDays",
        "value.amount",
        "value.currency",
        "dateSigned",
        "relatedProcesses.identifier",
        "relatedProcesses.relationship",
    ],
    "Organization": [
        "name",
        "id",
        "identifier.scheme",
        "identifier.id",
        "identifier.legalName",
        "identifier.uri",
        "address.streetAddress",
        "address.locality",
        "address.region",
        "address.postalCode",
        "address.countryName",
        "contactPoint.name",
        "contactPoint.email",
        "contactPoint.telephone",
        "contactPoint.faxNumber",
        "contactPoint.url",
        "roles",
        "details",
    ],
    "Address": [
        "streetAddress",
        "locality",
        "region",
        "postalCode",
        "countryName",
    ],
    "Item": [
        "id",
        "description",
        "classification.scheme",
        "classification.id",
        "classification.description",
        "classification.uri",
        "quantity",
        "unit.scheme",
        "unit.id",
        "unit.name",
        "unit.value.amount",
        "unit.value.currency",
        "unit.uri",
    ],
    "Classification": ["scheme", "id", "description", "uri"],
    "Value": ["amount", "currency"],
    "Period": ["startDate", "endDate", "maxExtentDate", "durationInDays"],
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def source_lookup(document: dict[str, Any]) -> dict[str, dict[str, Any]]:
    found: dict[str, dict[str, Any]] = {}
    for row in document["rows"]:
        if "Contracts_PrimeAwardSummaries.csv" not in str(row[6] or ""):
            continue
        columns = [part.strip() for part in str(row[7] or "").split(",")]
        for column in filter(None, columns):
            found.setdefault(
                column,
                {
                    "element": str(row[0] or "").strip(),
                    "definition": str(row[1] or "").strip(),
                    "grouping": str(row[3] or "").strip(),
                    "domain_values": str(row[4] or "").strip(),
                    "official_file": "Contracts_PrimeAwardSummaries.csv",
                },
            )
    return found


def build_source(dictionary: dict[str, Any]) -> list[dict[str, str]]:
    lookup = source_lookup(dictionary["document"])
    rows: list[dict[str, str]] = []
    for table, columns in SOURCE_FIELDS.items():
        for column in columns:
            if column not in lookup:
                raise KeyError(f"official source field not found: {column}")
            metadata = lookup[column]
            sample = " | ".join(metadata["domain_values"].splitlines()[:3])[:500]
            rows.append(
                {
                    "TableName": table,
                    "TableDescription": TABLE_DESCRIPTIONS[table],
                    "ColumnName": column,
                    "ColumnDescription": metadata["definition"],
                    "ColumnType": "",
                    "SampleValues": sample,
                    "DescriptionSource": (
                        "USAspending data dictionary API; element "
                        f"{metadata['element']}"
                    ),
                    "TableDescriptionStatus": "manually_written",
                    "ColumnDescriptionStatus": "source_provided",
                    "ColumnTypeStatus": "missing",
                    "SampleValuesStatus": ("source_provided" if sample else "missing"),
                }
            )
    return rows


def dereference(root: dict[str, Any], node: dict[str, Any]) -> dict[str, Any]:
    while "$ref" in node:
        ref = str(node["$ref"])
        if not ref.startswith("#/"):
            raise ValueError(f"external schema reference is not supported: {ref}")
        current: Any = root
        for key in ref[2:].split("/"):
            current = current[key]
        node = current
    return node


def property_node(
    root: dict[str, Any], object_type: str, property_path: str
) -> dict[str, Any]:
    node = root if object_type == "Release" else root["definitions"][object_type]
    node = dereference(root, node)
    for part in property_path.split("."):
        if node.get("type") == "array":
            node = node["items"]
        node = dereference(root, node)
        properties = node.get("properties", {})
        if part not in properties:
            raise KeyError(f"{object_type}.{property_path}: missing segment {part}")
        node = properties[part]
    return dereference(root, node)


def type_label(node: dict[str, Any]) -> str:
    value = node.get("type", "")
    if isinstance(value, list):
        return "|".join(str(item) for item in value)
    if value:
        return str(value)
    if "properties" in node:
        return "object"
    return "missing"


def build_target(schema: dict[str, Any]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for object_type, paths in TARGET_PATHS.items():
        object_node = (
            schema if object_type == "Release" else schema["definitions"][object_type]
        )
        for path in paths:
            node = property_node(schema, object_type, path)
            rows.append(
                {
                    "ObjectType": object_type,
                    "ObjectTypeDescription": str(
                        object_node.get("description")
                        or object_node.get("title")
                        or object_type
                    ),
                    "PropertyName": path,
                    "PropertyDescription": str(
                        node.get("description") or node.get("title") or ""
                    ),
                    "PropertyType": type_label(node),
                    "DefinitionSource": (
                        f"OCDS 1.1.5 canonical release schema; {object_type}.{path}"
                    ),
                    "DefinitionStatus": "source_provided",
                }
            )
    return rows


def main() -> None:
    dictionary_path = PUBLIC / "usaspending_data_dictionary.json"
    ocds_path = PUBLIC / "ocds_release_schema_1_1_5.json"
    dictionary = json.loads(dictionary_path.read_text(encoding="utf-8"))
    schema = json.loads(ocds_path.read_text(encoding="utf-8"))
    source_rows = build_source(dictionary)
    target_rows = build_target(schema)
    if len(source_rows) != 55:
        raise AssertionError(f"expected 55 source properties, got {len(source_rows)}")
    if not 50 <= len(target_rows) <= 150:
        raise AssertionError(f"target property count out of range: {len(target_rows)}")

    source_path = DATA / "source_schema.csv"
    target_path = DATA / "target_ontology.csv"
    write_csv(source_path, source_rows, list(source_rows[0]))
    write_csv(target_path, target_rows, list(target_rows[0]))
    manifest = {
        "source_properties": len(source_rows),
        "source_tables": len(SOURCE_FIELDS),
        "target_properties": len(target_rows),
        "target_object_types": len(TARGET_PATHS),
        "source_schema_sha256": sha256(source_path),
        "target_ontology_sha256": sha256(target_path),
        "input_sha256": {
            dictionary_path.name: sha256(dictionary_path),
            ocds_path.name: sha256(ocds_path),
        },
        "target_fixed_before_gold": True,
        "llm_generated_metadata": False,
    }
    path = DATA / "schema_manifest.json"
    path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
