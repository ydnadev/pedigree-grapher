# pedigree/models.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Set, Optional, Iterable


@dataclass
class Individual:
    individual_id: str
    father_id: str
    mother_id: str
    sex: str
    usgs_band_id: str
    hatch_year: str
    aux_id: str


class Pedigree:
    """Parse and query pedigree relationships."""

    def __init__(self, relationships: Dict[str, Individual] | None = None):
        self.relationships: Dict[str, Individual] = relationships or {}

    @classmethod
    def from_file(cls, ped_file) -> "Pedigree":
        """Create a Pedigree from an uploaded CSV-like file."""
        file_contents = ped_file.getvalue().decode("utf-8")
        relationships: Dict[str, Individual] = {}
        seen_lines: Set[str] = set()

        for raw_line in file_contents.split("\n"):
            line = raw_line.strip()
            if not line:
                continue
            if line in seen_lines:
                continue
            seen_lines.add(line)

            parts = line.split(",")
            if len(parts) < 7:
                continue

            (
                individual_id,
                father_id,
                mother_id,
                sex,
                usgs_band_id,
                hatch_year,
                aux_id,
            ) = parts

            sex_val = sex
            usgs_val = usgs_band_id if usgs_band_id != "0" else "N/A"
            hatch_val = hatch_year if hatch_year else "N/A"
            aux_val = aux_id if aux_id != "0" else "N/A"

            relationships[individual_id] = Individual(
                individual_id=individual_id,
                father_id=father_id,
                mother_id=mother_id,
                sex=sex_val,
                usgs_band_id=usgs_val,
                hatch_year=hatch_val,
                aux_id=aux_val,
            )

        return cls(relationships)

    def get_mates(self, individual_id: str) -> Set[str]:
        """Return mates (share at least one child) of an individual."""
        mates: Set[str] = set()
        if individual_id not in self.relationships:
            return mates

        for child in self.relationships.values():
            pid = child.father_id
            mid = child.mother_id

            if pid == individual_id and mid in self.relationships and mid != "0":
                mates.add(mid)
            if mid == individual_id and pid in self.relationships and pid != "0":
                mates.add(pid)

        return mates

    def filter_family(
        self, individual_id: Optional[str], filter_year: Optional[str] = None
    ) -> Dict[str, Individual]:
        """Return family subset around individual_id, optionally filtered by hatch_year."""
        if not individual_id or individual_id not in self.relationships:
            return self.relationships

        family: Dict[str, Individual] = {}
        focal = self.relationships[individual_id]
        family[individual_id] = focal

        father_id = focal.father_id
        mother_id = focal.mother_id

        if father_id in self.relationships and father_id != "0":
            family[father_id] = self.relationships[father_id]
        if mother_id in self.relationships and mother_id != "0":
            family[mother_id] = self.relationships[mother_id]

        mates = self.get_mates(individual_id)
        for mate_id in mates:
            family[mate_id] = self.relationships[mate_id]

        for child in self.relationships.values():
            cpid = child.father_id
            cmid = child.mother_id
            if (
                cpid == individual_id
                or cmid == individual_id
                or cpid in mates
                or cmid in mates
            ):
                if filter_year is None or child.hatch_year == filter_year:
                    family[child.individual_id] = child

        return family

