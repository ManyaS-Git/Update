class AudienceIntelligenceService:
    """Produces aggregate inferences only; every result includes evidence and confidence."""
    def inference(self, dimension: str, value: str, confidence: float, evidence: list[str]) -> dict:
        return {"dimension":dimension,"value":value,"confidence":confidence,"evidence":evidence,"probabilistic":dimension in {"age_bracket","geography","professional_interest"}}
