"""SNOMED CT (Veterinary Extension) lookup for common ER presentations.

Veterinary medicine has no equivalent of ICD-10-CM/CPT — those are human
billing code sets tied to CMS/insurance claims that vet practices don't
submit to. SNOMED CT's veterinary extension (VetSCT), maintained by the
Veterinary Terminology Services Laboratory at Virginia Tech, is the closest
real, standardized fit.

The concept IDs below are NOT verified: VetSCT's browser (https://vtsl.vetmed.vt.edu/)
requires free registration, and the NLM's UMLS distribution of SNOMEDCT_VET
requires a license — neither is something to scrape or guess numeric IDs
against. Shipping a fabricated-looking numeric code would be worse than
shipping none, so every entry here is explicitly marked unverified until a
human checks it against VTSL (or this tool is replaced by a live terminology
server / API call — tracked as a follow-up task).
"""

from dataclasses import dataclass
from typing import Any

from claude_agent_sdk import tool


@dataclass(frozen=True)
class SnomedEntry:
    preferred_term: str
    concept_id: str | None  # None until verified against an authoritative source
    verified: bool


# Small, hand-picked starter set of common ER presentations — not remotely
# exhaustive. Meant to unblock the agent pipeline end-to-end while the real
# terminology-server integration is built.
_TABLE: dict[str, SnomedEntry] = {
    "canine parvovirus": SnomedEntry("Canine parvoviral enteritis", None, verified=False),
    "gdv": SnomedEntry("Gastric dilation-volvulus of dog", None, verified=False),
    "bloat": SnomedEntry("Gastric dilation-volvulus of dog", None, verified=False),
    "foreign body ingestion": SnomedEntry("Gastrointestinal foreign body", None, verified=False),
    "hit by car": SnomedEntry("Motor vehicle accident injury of animal", None, verified=False),
    "hbc": SnomedEntry("Motor vehicle accident injury of animal", None, verified=False),
    "feline urinary obstruction": SnomedEntry("Urethral obstruction of cat", None, verified=False),
    "pyometra": SnomedEntry("Pyometra", None, verified=False),
}


@tool(
    "snomed_lookup",
    "Look up a candidate SNOMED CT (veterinary extension) term for a clinical finding.",
    {"query": str},
)
async def snomed_lookup(args: dict[str, Any]) -> dict[str, Any]:
    entry = _TABLE.get(args["query"].strip().lower())
    if entry is None:
        text = (
            f"No entry for {args['query']!r} in the local starter table. "
            "Do not guess a code — report this finding as uncoded."
        )
        return {"content": [{"type": "text", "text": text}]}

    caveat = (
        " UNVERIFIED concept ID — do not use for real coding until checked "
        "against the VTSL SNOMED CT veterinary extension browser."
        if not entry.verified
        else ""
    )
    text = f"{entry.preferred_term} (concept_id={entry.concept_id or 'unknown'}).{caveat}"
    return {"content": [{"type": "text", "text": text}]}


snomed_lookup_tool = snomed_lookup
