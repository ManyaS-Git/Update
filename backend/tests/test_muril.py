import pytest
from app.services.muril_service import get_muril_service

def test_muril_multilingual_representations():
    muril = get_muril_service()

    # 1. English
    en_rep = muril.extract_representation("The railway safety regulations need strict independent oversight.")
    assert en_rep.language == "english"
    assert en_rep.script == "latin"
    assert len(en_rep.representation_vector) == 16
    assert en_rep.confidence > 0.5

    # 2. Hindi Devanagari
    hi_rep = muril.extract_representation("रेलवे सुरक्षा नियम बहुत ज़रूरी हैं और इनका पालन होना चाहिए।")
    assert hi_rep.language == "hindi"
    assert hi_rep.script == "devanagari"
    assert len(hi_rep.representation_vector) == 16
    assert hi_rep.confidence >= 0.9

    # 3. Hinglish (Latin transliteration)
    hing_rep = muril.extract_representation("yeh policy bilkul sahi hai aur students ko support milna chahiye")
    assert hing_rep.language == "hinglish"
    assert hing_rep.script in ("latin_transliterated", "mixed_devanagari_latin")
    assert len(hing_rep.representation_vector) == 16
    assert hing_rep.confidence >= 0.7
