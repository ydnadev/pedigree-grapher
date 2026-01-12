# pedigree/graph.py
from __future__ import annotations

from typing import Dict, Optional

from graphviz import Digraph
from .models import Pedigree, Individual


class PedigreeGraphBuilder:
    """Turn a Pedigree (or subset) into a PNG graph."""

    def __init__(self, pedigree: Pedigree):
        self.pedigree = pedigree

    def _edge_color(self, parent: Individual | None) -> str:
        if parent is None:
            return "gray"
        if parent.sex == "1":
            return "blue"
        if parent.sex == "2":
            return "red"
        return "gray"

    def build_png(
        self,
        relationships: Dict[str, Individual],
        focus_id: Optional[str] = None,
        dpi: int = 1000,
    ) -> bytes | None:
        if not relationships:
            return None

        dot = Digraph(format="png")
        dot.attr(rankdir="TB", nodesep="0.2", ranksep="0.6", size="8,8!")
        dot.attr("graph", dpi=str(dpi))
        drawn: set[str] = set()

        def create_node(iid: str):
            if iid in drawn or iid not in relationships:
                return
            info = relationships[iid]
            lines = [f"Individual: {iid}"]
            if info.hatch_year and info.hatch_year != "N/A":
                lines.append(f"Hatch Year: {info.hatch_year}")
            if info.usgs_band_id != "":
                lines.append(f"Primary ID: {info.usgs_band_id}")
            if info.aux_id != "":
                lines.append(f"Aux ID: {info.aux_id}")
            label = "\\n".join(lines)

            shape = "egg"
            fillcolor = "gray"
            if info.sex == "1":
                shape = "box"
                fillcolor = "lightblue"
            elif info.sex == "2":
                shape = "ellipse"
                fillcolor = "lightpink"

            dot.node(iid, label=label, shape=shape, style="filled", fillcolor=fillcolor)
            drawn.add(iid)

        if focus_id and focus_id in relationships:
            focal = relationships[focus_id]
            father = relationships.get(focal.father_id)
            mother = relationships.get(focal.mother_id)
            mates = self.pedigree.get_mates(focus_id)

            if father and mother and father.individual_id != "0" and mother.individual_id != "0":
                with dot.subgraph() as parents_sub:
                    parents_sub.attr(rank="same")
                    create_node(father.individual_id)
                    create_node(mother.individual_id)
                dot.edge(
                    father.individual_id, focus_id, color=self._edge_color(father)
                )
                dot.edge(
                    mother.individual_id, focus_id, color=self._edge_color(mother)
                )
            else:
                if father and father.individual_id != "0":
                    create_node(father.individual_id)
                    dot.edge(
                        father.individual_id, focus_id, color=self._edge_color(father)
                    )
                if mother and mother.individual_id != "0":
                    create_node(mother.individual_id)
                    dot.edge(
                        mother.individual_id, focus_id, color=self._edge_color(mother)
                    )

            with dot.subgraph() as main_sub:
                main_sub.attr(rank="same")
                create_node(focus_id)
                for mate in mates:
                    create_node(mate)

            for child in relationships.values():
                cpid = child.father_id
                cmid = child.mother_id
                if (cpid == focus_id or cpid in mates) or (
                    cmid == focus_id or cmid in mates
                ):
                    create_node(child.individual_id)
                    if cpid == focus_id or cpid in mates:
                        dot.edge(
                            cpid,
                            child.individual_id,
                            color=self._edge_color(relationships.get(cpid)),
                        )
                    if cmid == focus_id or cmid in mates:
                        dot.edge(
                            cmid,
                            child.individual_id,
                            color=self._edge_color(relationships.get(cmid)),
                        )
        else:
            for iid in relationships:
                create_node(iid)
            for child in relationships.values():
                pid = relationships.get(child.father_id)
                mid = relationships.get(child.mother_id)
                if pid and pid.individual_id != "0":
                    dot.edge(
                        pid.individual_id,
                        child.individual_id,
                        color=self._edge_color(pid),
                    )
                if mid and mid.individual_id != "0":
                    dot.edge(
                        mid.individual_id,
                        child.individual_id,
                        color=self._edge_color(mid),
                    )

        return dot.pipe(format="png")

