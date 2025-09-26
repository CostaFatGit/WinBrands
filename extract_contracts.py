#!/usr/bin/env python3
"""Extract contract details from PDF order forms and write them to CSV."""
from __future__ import annotations

import argparse
import csv
import re
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from pypdf import PdfReader

FIELD_ORDER: List[str] = [
    "pdf_filename",
    "order_form_number",
    "customer_name",
    "customer_address",
    "subscription_term_start_date",
    "subscription_term_months",
    "capacity_currency",
    "capacity_amount",
    "credit_discount_percent",
    "sales_representative",
    "billing_address",
    "billing_email",
    "total_capacity_fees_currency",
    "total_capacity_fees_amount",
    "capacity_payment_terms",
    "on_demand_payment_terms",
    "capacity_billing_frequency",
    "on_demand_billing_frequency",
    "edition",
    "cloud_provider",
    "region",
    "capacity_credit_price_currency",
    "capacity_credit_price",
    "capacity_storage_currency",
    "capacity_storage_price",
    "capacity_storage_tier",
    "docu_sign_envelope_id",
]


def main(argv: Optional[Iterable[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Extract Snowflake capacity order form data into CSV.")
    parser.add_argument(
        "--pdf",
        nargs="*",
        help="Path(s) to PDF files. Defaults to all PDFs in the current working directory.",
    )
    parser.add_argument(
        "--output",
        default="contracts.csv",
        help="Output CSV file path (default: contracts.csv).",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    pdf_paths = _resolve_pdf_paths(args.pdf)
    if not pdf_paths:
        raise SystemExit("No PDF files found to process.")

    records = [extract_contract_info(pdf_path) for pdf_path in pdf_paths]

    output_path = Path(args.output)
    write_to_csv(records, output_path)
    print(f"Wrote {len(records)} record(s) to {output_path}")


def _resolve_pdf_paths(raw_paths: Optional[List[str]]) -> List[Path]:
    if raw_paths:
        return [Path(path).resolve() for path in raw_paths]
    return sorted(Path.cwd().glob("*.pdf"))


def extract_contract_info(pdf_path: Path) -> Dict[str, Any]:
    reader = PdfReader(str(pdf_path))
    pages_text = [page.extract_text() or "" for page in reader.pages]
    text = "\n".join(pages_text)

    record: Dict[str, Any] = {field: None for field in FIELD_ORDER}
    record["pdf_filename"] = pdf_path.name

    _populate_customer_details(record, text)
    _populate_subscription_details(record, text)
    _populate_payment_terms(record, text)
    _populate_service_details(record, text)
    _populate_metadata(record, text)

    return record


def _populate_customer_details(record: Dict[str, Any], text: str) -> None:
    ship_block = _extract_block(text, "Customer (Ship To)", "Subscription Term Start Date")
    if ship_block:
        lines = _clean_lines(ship_block)
        if lines:
            record["customer_name"] = lines[0]
            if len(lines) > 1:
                record["customer_address"] = "\n".join(lines[1:])

    billing_block = _extract_block(text, "Customer Billing Address", "Billing Email")
    if billing_block:
        lines = _clean_lines(billing_block)
        if lines:
            record["billing_address"] = "\n".join(lines)

    billing_email = _search_single_line_value(text, "Billing Email")
    if billing_email:
        record["billing_email"] = billing_email


def _populate_subscription_details(record: Dict[str, Any], text: str) -> None:
    start_date_str = _search_single_line_value(text, "Subscription Term Start Date")
    if start_date_str:
        parsed_date = _parse_date(start_date_str)
        record["subscription_term_start_date"] = parsed_date if parsed_date else start_date_str

    term_str = _search_single_line_value(text, "Subscription Term", skip_prefixes=("Start",))
    if term_str:
        match = re.search(r"(\d+)", term_str)
        if match:
            record["subscription_term_months"] = int(match.group(1))

    capacity_value = _search_single_line_value(text, "Capacity", skip_prefixes=("Commitment.", "for", "order"))
    if capacity_value:
        currency, amount = _parse_currency_amount(capacity_value)
        record["capacity_currency"] = currency
        record["capacity_amount"] = amount

    credit_discount = _search_single_line_value(text, "Credit Discount")
    if credit_discount:
        match = re.search(r"([\d.,]+)", credit_discount)
        if match:
            record["credit_discount_percent"] = float(match.group(1).replace(",", ""))

    sales_rep = _search_single_line_value(text, "Snowflake Sales Representative")
    if sales_rep:
        record["sales_representative"] = sales_rep

    order_form_number = _search_single_line_value(text, "Order Form #")
    if order_form_number:
        record["order_form_number"] = order_form_number


def _populate_payment_terms(record: Dict[str, Any], text: str) -> None:
    capacity_fees_line = _search_line(text, "Total Capacity Fees Due")
    if capacity_fees_line:
        value_part = capacity_fees_line.replace("Total Capacity Fees Due", "", 1).strip()
        capacity_segment = value_part.split("  ")[0].strip() if "  " in value_part else value_part
        currency, amount = _parse_currency_amount(capacity_segment)
        record["total_capacity_fees_currency"] = currency
        record["total_capacity_fees_amount"] = amount

    payment_terms_line = _search_line(text, "Payment Terms")
    if payment_terms_line:
        value_part = payment_terms_line.replace("Payment Terms", "", 1).strip()
        capacity_terms, on_demand_terms = _split_table_row(value_part)
        if capacity_terms:
            record["capacity_payment_terms"] = capacity_terms
        if on_demand_terms:
            record["on_demand_payment_terms"] = on_demand_terms

    billing_frequency_line = _search_line(text, "Billing Frequency")
    if billing_frequency_line:
        value_part = billing_frequency_line.replace("Billing Frequency", "", 1).strip()
        capacity_freq, on_demand_freq = _split_table_row(value_part, prefer_first_token=True)
        if capacity_freq:
            record["capacity_billing_frequency"] = capacity_freq
        if on_demand_freq:
            record["on_demand_billing_frequency"] = on_demand_freq


def _populate_service_details(record: Dict[str, Any], text: str) -> None:
    lines = _clean_lines(text)
    try:
        header_index = lines.index(
            "Edition Cloud Provider Region Capacity Credit Price Capacity Storage Pricing Capacity Storage Tier"
        )
    except ValueError:
        return

    if header_index + 1 >= len(lines):
        return

    data_line = lines[header_index + 1]
    tokens = data_line.split()
    if len(tokens) < 7:
        return

    record["edition"] = tokens[0]
    record["cloud_provider"] = tokens[1]
    record["region"] = tokens[2]

    record["capacity_credit_price_currency"] = tokens[3]
    record["capacity_credit_price"] = _parse_float(tokens[4])
    record["capacity_storage_currency"] = tokens[5]
    record["capacity_storage_price"] = _parse_float(tokens[6])
    if len(tokens) > 7:
        record["capacity_storage_tier"] = " ".join(tokens[7:])


def _populate_metadata(record: Dict[str, Any], text: str) -> None:
    match = re.search(r"Docusign Envelope ID:\s*([A-Z0-9-]+)", text, flags=re.IGNORECASE)
    if match:
        record["docu_sign_envelope_id"] = match.group(1)


def write_to_csv(records: List[Dict[str, Any]], output_path: Path) -> None:
    with output_path.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=FIELD_ORDER)
        writer.writeheader()
        for record in records:
            writer.writerow({field: _format_csv_value(record.get(field)) for field in FIELD_ORDER})


def _format_csv_value(value: Any) -> Any:
    if value is None:
        return ""
    if isinstance(value, date):
        return value.isoformat()
    return value


def _clean_lines(text: str) -> List[str]:
    cleaned: List[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.endswith("United StatesX"):
            stripped = stripped[:-1].strip()
        cleaned.append(stripped)
    return cleaned


def _extract_block(text: str, start_marker: str, end_marker: str) -> Optional[str]:
    pattern = re.compile(
        re.escape(start_marker) + r"\s*(.*?)\s*" + re.escape(end_marker), flags=re.DOTALL | re.IGNORECASE
    )
    match = pattern.search(text)
    return match.group(1) if match else None


def _search_single_line_value(
    text: str, label: str, skip_prefixes: Optional[Tuple[str, ...]] = None
) -> Optional[str]:
    label_lower = label.lower()
    skip = tuple(prefix.lower() for prefix in (skip_prefixes or ()))
    target = label_lower + " "
    for line in text.splitlines():
        stripped = line.strip()
        lower = stripped.lower()
        if lower.startswith(target):
            remainder = stripped[len(label):].strip()
            if skip and any(remainder.lower().startswith(prefix) for prefix in skip):
                continue
            return remainder
    return None


def _search_line(text: str, label: str) -> Optional[str]:
    for line in text.splitlines():
        if label in line:
            return line.strip()
    return None


def _split_table_row(value: str, prefer_first_token: bool = False) -> Tuple[Optional[str], Optional[str]]:
    value = value.strip()
    if not value:
        return None, None

    if "  " in value:
        left, right = value.split("  ", 1)
        return left.strip() or None, right.strip() or None

    tokens = value.split()
    if prefer_first_token and tokens:
        left = tokens[0]
        right = " ".join(tokens[1:]).strip() or None
        return left, right

    if len(tokens) % 2 == 0 and tokens:
        midpoint = len(tokens) // 2
        left = " ".join(tokens[:midpoint]).strip()
        right = " ".join(tokens[midpoint:]).strip()
        return left or None, right or None

    return value or None, None


def _parse_currency_amount(value: str) -> Tuple[Optional[str], Optional[float]]:
    match = re.search(r"([A-Z]{3})\s*([\d,]+(?:\.\d+)?)", value)
    if match:
        currency = match.group(1)
        amount = _parse_float(match.group(2))
        return currency, amount
    return None, None


def _parse_float(value: str) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value.replace(",", ""))
    except ValueError:
        return None


def _parse_date(value: str) -> Optional[date]:
    for fmt in ("%d %B %Y", "%B %d %Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


if __name__ == "__main__":
    main()
