"""STRAT-026 v0.6.2 public architecture excerpt.

This module demonstrates reviewable invariants from the research system. It is
not the complete production backtest and deliberately excludes private data
adapters, the full parameter set, and proprietary execution details.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Literal, Sequence

Side = Literal["long", "short"]


@dataclass(frozen=True)
class ContractSnapshot:
    instrument: str
    product: str
    close: float
    delivery_anchor: float
    margin_rate: float
    months_to_delivery: int


@dataclass(frozen=True)
class Candidate:
    instrument: str
    product: str
    side: Side
    deviation_score: float
    margin_rate: float


@dataclass(frozen=True)
class PositionRisk:
    product: str
    side: Side
    margin: float
    equity: float

    @property
    def risk_ratio(self) -> float:
        if self.equity <= 0:
            raise ValueError("equity must be positive")
        return self.margin / self.equity


def deviation_signal(snapshot: ContractSnapshot) -> Side | None:
    """Map a sufficiently large futures-anchor deviation to a trade side."""
    if snapshot.close <= 0 or snapshot.delivery_anchor <= 0:
        raise ValueError("prices must be positive")
    if snapshot.margin_rate <= 0:
        raise ValueError("margin_rate must be positive")
    if not 0 <= snapshot.months_to_delivery <= 6:
        return None

    gap = snapshot.close / snapshot.delivery_anchor - 1.0
    threshold = 2.0 * snapshot.margin_rate
    if gap >= threshold:
        return "short"
    if gap <= -threshold:
        return "long"
    return None


def rank_candidate(snapshot: ContractSnapshot) -> Candidate | None:
    """Build the product-level ranking score after the primary screen."""
    side = deviation_signal(snapshot)
    if side is None or snapshot.months_to_delivery == 0:
        return None
    score = abs(snapshot.close - snapshot.delivery_anchor) / snapshot.months_to_delivery
    return Candidate(
        instrument=snapshot.instrument,
        product=snapshot.product,
        side=side,
        deviation_score=score,
        margin_rate=snapshot.margin_rate,
    )


def select_product_winners(snapshots: Iterable[ContractSnapshot]) -> list[Candidate]:
    """Keep one deterministic maximum-score candidate for each product."""
    winners: dict[str, Candidate] = {}
    for snapshot in snapshots:
        candidate = rank_candidate(snapshot)
        if candidate is None:
            continue
        current = winners.get(candidate.product)
        if current is None or (
            candidate.deviation_score,
            candidate.instrument,
        ) > (
            current.deviation_score,
            current.instrument,
        ):
            winners[candidate.product] = candidate
    return sorted(winners.values(), key=lambda item: (item.product, item.instrument))


def account_risk(positions: Sequence[PositionRisk]) -> dict[str, float]:
    """Return long, short, net-direction, and gross margin risk ratios."""
    if not positions:
        return {"long": 0.0, "short": 0.0, "net": 0.0, "gross": 0.0}
    equity = positions[0].equity
    if equity <= 0 or any(abs(position.equity - equity) > 1e-8 for position in positions):
        raise ValueError("all positions must share one positive account equity")

    long_margin = sum(position.margin for position in positions if position.side == "long")
    short_margin = sum(position.margin for position in positions if position.side == "short")
    return {
        "long": long_margin / equity,
        "short": short_margin / equity,
        "net": abs(long_margin - short_margin) / equity,
        "gross": (long_margin + short_margin) / equity,
    }


def bundle_conflict(
    candidate: Candidate,
    held_positions: Sequence[PositionRisk],
    product_bundles: dict[str, set[str]],
    heavy_threshold: float,
) -> bool:
    """Reject same-side candidates sharing a bundle with a heavy position."""
    candidate_bundles = {
        name for name, members in product_bundles.items() if candidate.product in members
    }
    if not candidate_bundles:
        return False

    for position in held_positions:
        if position.side != candidate.side or position.risk_ratio <= heavy_threshold:
            continue
        held_bundles = {
            name for name, members in product_bundles.items() if position.product in members
        }
        if candidate_bundles & held_bundles:
            return True
    return False
