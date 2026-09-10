# program.health.oracle.beast3.py
# Beast System 3.0 — Deterministic Wellbeing Oracle v2

from dataclasses import dataclass, field
import time
import hashlib

# Oracle input categories
ORACLE_INPUTS = {
    "vitals": ["heart_rate", "blood_pressure", "oxygen", "temperature"],
    "housing": ["stability_score", "occupancy_status", "risk_level"],
    "education": ["attendance", "performance", "continuity"],
    "finance": ["income_stability", "benefit_access", "emergency_funds"],
    "community": ["engagement_score", "support_network", "civic_alignment"],
    "care": ["referrals", "followups", "continuity_score"],
    "behavior": ["stress_level", "sleep_quality", "activity_score"]
}

@dataclass
class OraclePacket:
    family_id: str
    inputs: dict
    ts: float = field(default_factory=time.time)
    hash: str = ""

    def finalize(self):
        serialized = f"{self.family_id}{self.inputs}{self.ts}".encode("utf-8")
        self.hash = hashlib.sha256(serialized).hexdigest()

@dataclass
class OracleProfile:
    family_id: str
    packets: list = field(default_factory=list)
    last_update: float = field(default_factory=time.time)

    def add_packet(self, inputs: dict):
        packet = OraclePacket(self.family_id, inputs)
        packet.finalize()
        self.packets.append(packet)
        self.last_update = packet.ts

class WellbeingOracleEngine:
    def __init__(self, kernel):
        self.kernel = kernel
        self.oracles = {}

    def create_oracle(self, family_id: str):
        profile = OracleProfile(family_id)
        self.oracles[family_id] = profile

        return self.kernel.dispatch(
            module="health.oracle",
            action="create_oracle",
            payload={"family_id": family_id}
        )

    def submit_inputs(self, family_id: str, inputs: dict):
        if family_id not in self.oracles:
            raise ValueError("Oracle profile not found")

        # Validate input categories
        validated = {}
        for category, fields in ORACLE_INPUTS.items():
            if category in inputs:
                validated[category] = {
                    field: inputs[category].get(field, None)
                    for field in fields
                }

        profile = self.oracles[family_id]
        profile.add_packet(validated)

        return self.kernel.dispatch(
            module="health.oracle",
            action="submit_inputs",
            payload={"family_id": family_id, "inputs": validated}
        )

    def get_packets(self, family_id: str):
        if family_id not in self.oracles:
            return None
        return self.oracles[family_id].packets
