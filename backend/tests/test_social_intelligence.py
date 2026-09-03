from fastapi.testclient import TestClient
from app.main import app
from app.services.intelligence import CommentIntelligenceService
from app.models.schemas import CommentInput
from app.services.database import preview_analytics
from app.services.ingestion import _hash_author
import hashlib

client=TestClient(app)

def test_hindi_and_hinglish_language_detection():
    service=CommentIntelligenceService()
    hindi=service.analyse(CommentInput(text="यह नीति बहुत अच्छी और ज़रूरी है"))
    hinglish=service.analyse(CommentInput(text="yeh policy sahi hai aur support karna chahiye"))
    assert hindi.language=="hindi" and hindi.sentiment=="positive"
    assert hinglish.language=="hinglish" and hinglish.stance=="supportive"

def test_sentiment_stance_and_hate_are_separate_labels():
    result=client.post("/api/classify",json={"text":"I oppose this unfair policy, but do not attack anyone.","context":"reservation policy"}).json()
    assert result["sentiment"] in {"negative","neutral"}
    assert result["stance"]=="opposing"
    assert result["safety"]=="normal"

def test_hate_safety_label():
    result=client.post("/api/classify",json={"text":"Those people are subhuman and should go back"}).json()
    assert result["safety"]=="hate"

def test_explicit_metadata_only_for_sensitive_inference():
    unknown=client.post("/api/classify",json={"text":"I am a student and support equality"}).json()
    known=client.post("/api/classify",json={"text":"I support equality","public_signals":{"location":"Delhi NCR","age_bracket":"18-24"}}).json()
    assert unknown["geography"] is None and unknown["age_bracket"] is None
    assert known["geography"]=="Delhi NCR" and known["age_bracket"]=="18-24"

def test_connector_capability_contract():
    rows=client.get("/api/connectors").json()
    assert {row["platform"] for row in rows}=={"x","youtube","reddit","facebook","instagram"}
    assert next(row for row in rows if row["platform"]=="instagram")["requires_targets"] is True

def test_model_status_never_mislabels_fallback_as_muril():
    status=client.get("/api/models/status").json()["sentiment"]
    assert status["active_provider"] in {"not_loaded","local_muril","dedicated_endpoint","heuristic_fallback","unavailable"}
    if status["active_provider"]=="heuristic_fallback":
        result=client.post("/api/classify",json={"text":"yeh policy sahi hai"}).json()
        assert result["model_name"]=="multilingual-heuristic-fallback"

def test_signal_quality_is_returned_with_classification():
    low=client.post("/api/classify",json={"text":"BINOD"}).json()
    high=client.post("/api/classify",json={"text":"The reservation policy affects student education and equal opportunity."}).json()
    assert low["signal_classification"]=="LOW_SIGNAL"
    assert high["signal_quality"]>low["signal_quality"]

def test_comment_summary_has_privacy_disclosure():
    summary=client.get("/api/comments/summary").json()
    assert "not guessed" in summary["disclosure"]
    assert "signal_quality" in summary

def test_new_story_context_is_complete_and_evidence_scoped():
    analytics=preview_analytics("Students protest new education policy","Education","Example News")
    assert analytics["brief"]["insight"]
    assert analytics["drivers"] and analytics["trends"]
    assert analytics["audience"]["language"]["confidence"]=="High"
    assert analytics["audience"]["geography"]["confidence"]=="Unavailable"
    assert analytics["audience"]["confidence"]["topics"]=="Medium"
    assert analytics["confidence"]["analysis_scope"]=="story_context"

def test_learning_status_contract():
    status=client.get("/api/learning/status")
    assert status.status_code==200
    assert {"human_labels","feedback_events","collected_comments"}<=status.json()["counts"].keys()

def test_author_identifier_uses_keyed_privacy_hash():
    value="public-user-123"
    assert _hash_author(value)!=hashlib.sha256(f"updates-public-author:{value}".encode()).hexdigest()
    assert _hash_author(value)==_hash_author(value)

def test_security_headers_and_input_validation():
    response=client.get("/api/topics/reservation-protest")
    assert response.headers["x-content-type-options"]=="nosniff"
    assert response.headers["x-frame-options"]=="DENY"
    invalid=client.post("/api/stories",json={"title":"Unsafe story","category":"News","summary":"A sufficiently long test summary.","image":"javascript:alert(1)","topic_slug":"reservation-protest"})
    assert invalid.status_code==422

def test_oversized_request_is_rejected_before_parsing():
    response=client.post("/api/classify",content=b"x"*1_000_001,headers={"content-type":"application/json"})
    assert response.status_code==413
