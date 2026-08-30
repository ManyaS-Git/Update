from __future__ import annotations
from dataclasses import dataclass
from functools import lru_cache
import importlib.util,math,os,re,threading
import httpx
from app.core.config import Settings,get_settings
from app.models.schemas import CommentInput,CommentIntelligence
from app.services.csqe import CSQEService

@dataclass
class SentimentPrediction:
    label:str;score:float;model:str

@dataclass
class SafetyPrediction:
    label:str;score:float;evidence:list[str];model:str

class MuRILSentimentProvider:
    _pipeline=None
    _lock=threading.Lock()
    _last_active="not_loaded"
    _last_error:str|None=None
    def __init__(self,settings:Settings|None=None):
        self.settings=settings or get_settings();self.last_error:str|None=None
        os.environ.setdefault("HF_HUB_DISABLE_XET","1");os.environ.setdefault("HF_HOME",self.settings.hf_model_cache)
    def predict(self,text:str)->SentimentPrediction:
        provider=self.settings.sentiment_provider
        if provider in {"auto","local"} and importlib.util.find_spec("transformers") and importlib.util.find_spec("torch"):
            try:
                if MuRILSentimentProvider._pipeline is None:
                    with MuRILSentimentProvider._lock:
                        if MuRILSentimentProvider._pipeline is None:
                            from transformers import AutoModelForSequenceClassification,AutoTokenizer,pipeline
                            tokenizer=AutoTokenizer.from_pretrained(self.settings.hf_sentiment_model,token=self.settings.hf_token,cache_dir=self.settings.hf_model_cache)
                            model=AutoModelForSequenceClassification.from_pretrained(self.settings.hf_sentiment_model,token=self.settings.hf_token,cache_dir=self.settings.hf_model_cache)
                            MuRILSentimentProvider._pipeline=pipeline("text-classification",model=model,tokenizer=tokenizer,device=self.settings.model_device)
                result=MuRILSentimentProvider._pipeline(text[:4000],top_k=3)
                rows=result[0] if result and isinstance(result[0],list) else result
                prediction=self._prediction(rows,self.settings.hf_sentiment_model);MuRILSentimentProvider._last_active="local_muril";MuRILSentimentProvider._last_error=None;return prediction
            except Exception as exc:
                self.last_error=f"local MuRIL unavailable: {exc}";MuRILSentimentProvider._last_error=self.last_error
                if provider=="local":raise
        if provider in {"auto","endpoint"} and self.settings.hf_inference_endpoint_url:
            try:
                headers={"Authorization":f"Bearer {self.settings.hf_token}"} if self.settings.hf_token else {}
                response=httpx.post(self.settings.hf_inference_endpoint_url,headers=headers,json={"inputs":text},timeout=45);response.raise_for_status();payload=response.json();rows=payload[0] if payload and isinstance(payload[0],list) else payload
                prediction=self._prediction(rows,f"endpoint:{self.settings.hf_sentiment_model}");MuRILSentimentProvider._last_active="dedicated_endpoint";MuRILSentimentProvider._last_error=None;return prediction
            except Exception as exc:
                self.last_error=f"inference endpoint unavailable: {exc}";MuRILSentimentProvider._last_error=self.last_error
                if provider=="endpoint":raise
        MuRILSentimentProvider._last_active="heuristic_fallback";return self._heuristic(text)
    @staticmethod
    def _prediction(rows:list[dict],model:str)->SentimentPrediction:
        best=max(rows,key=lambda item:item["score"]);label=str(best["label"]).lower().replace(" ","_")
        mapping={"label_0":"negative","label_1":"neutral","label_2":"positive","negative":"negative","neutral":"neutral","positive":"positive"}
        mapped=mapping.get(label)
        if not mapped:raise ValueError(f"Unsupported sentiment label from model: {label}")
        return SentimentPrediction(mapped,float(best["score"]),model)
    def _heuristic(self,text:str)->SentimentPrediction:
        lowered=text.lower();positive=("good","great","support","fair","justice","right","achi","accha","sahi","samarthan","ज़रूरी","अच्छा","समर्थन");negative=("bad","wrong","unfair","hate","against","galat","bekar","नफ़रत","गलत","विरोध")
        contains=lambda term:bool(re.search(rf"(?<![a-z]){re.escape(term)}(?![a-z])",lowered)) if term.isascii() else term in lowered
        pos=sum(contains(word) for word in positive);neg=sum(contains(word) for word in negative)
        if pos>neg:return SentimentPrediction("positive",min(.9,.58+.08*pos),"multilingual-heuristic-fallback")
        if neg>pos:return SentimentPrediction("negative",min(.9,.58+.08*neg),"multilingual-heuristic-fallback")
        return SentimentPrediction("neutral",.55,"multilingual-heuristic-fallback")

DEVANAGARI=re.compile(r"[\u0900-\u097f]")
LATIN=re.compile(r"[A-Za-z]")
HINGLISH={"hai","hain","ho","nahi","kya","kyu","kyun","acha","accha","sahi","galat","hume","humko","main","tum","aap","yeh","yaar","bahut","bilkul","karna","karte","karo","chahiye","aur","lekin","bewakoof","bakwas","samarthan","virodh"}
SUPPORT={"support","agree","necessary","justice","representation","equal opportunity","samarthan","sahi","zaroori","समर्थन","सही","न्याय","ज़रूरी"}
OPPOSE={"oppose","against","unfair","remove","wrong","galat","virodh","नहीं चाहिए","गलत","विरोध"}
HATE={"subhuman","exterminate","kill all","go back","जाति की गाली","मार डालो"}
TOXIC={"idiot","stupid","moron","shut up","bewakoof","bakwas","बेवकूफ","बकवास"}
INTERESTS={"Education & admissions":{"college","student","admission","exam","seat","school","शिक्षा","छात्र"},"Employment":{"job","employment","vacancy","recruitment","naukri","नौकरी"},"Law & policy":{"court","constitution","bill","policy","law","कानून","संविधान"},"Social justice":{"justice","equality","rights","caste","dalit","न्याय","समानता","जाति"},"Economy":{"economy","income","business","economic","अर्थव्यवस्था"}}

def detect_language(text:str)->tuple[str,float,list[str]]:
    has_dev=bool(DEVANAGARI.search(text));has_latin=bool(LATIN.search(text));tokens=set(re.findall(r"[a-z]+",text.lower()));markers=sorted(tokens&HINGLISH)
    if has_dev and has_latin:return "hinglish",.92,["mixed Devanagari and Latin scripts"]
    if has_dev:return "hindi",.95,["Devanagari script"]
    if len(markers)>=2:return "hinglish",min(.9,.58+.08*len(markers)),[f"romanised Hindi markers: {', '.join(markers[:5])}"]
    if has_latin:return "english",.82,["Latin script without strong Hinglish markers"]
    return "other",.45,["insufficient script evidence"]

def classify_stance(text:str,context:str|None)->tuple[str,float,list[str]]:
    lowered=f"{context or ''} {text}".lower();support=sorted(x for x in SUPPORT if x in lowered);oppose=sorted(x for x in OPPOSE if x in lowered)
    if "?" in text and not support and not oppose:return "questioning",.78,["question form"]
    if len(support)>len(oppose):return "supportive",min(.92,.62+.06*len(support)),support[:5]
    if len(oppose)>len(support):return "opposing",min(.92,.62+.06*len(oppose)),oppose[:5]
    return "neutral",.52,["no reliable topic-position cue"]

def classify_safety(text:str)->tuple[str,float,list[str]]:
    lowered=text.lower();hate=sorted(x for x in HATE if x in lowered);toxic=sorted(x for x in TOXIC if x in lowered)
    if hate:return "hate",.82,hate
    if toxic:return "toxic",.76,toxic
    return "normal",.7,["no configured hate/toxicity cue"]

class MuRILSafetyProvider:
    _pipeline=None
    _lock=threading.Lock()
    _last_active="not_loaded"
    _last_error:str|None=None
    def __init__(self,settings:Settings|None=None):self.settings=settings or get_settings()
    def predict(self,text:str)->SafetyPrediction:
        heuristic_label,heuristic_score,heuristic_evidence=classify_safety(text)
        if heuristic_label=="hate":return SafetyPrediction("hate",heuristic_score,heuristic_evidence,"hate-cue-plus-indic-safety-policy")
        provider=self.settings.safety_provider
        if provider in {"auto","local"} and importlib.util.find_spec("transformers") and importlib.util.find_spec("torch"):
            try:
                if MuRILSafetyProvider._pipeline is None:
                    with MuRILSafetyProvider._lock:
                        if MuRILSafetyProvider._pipeline is None:
                            from transformers import AutoModelForSequenceClassification,AutoTokenizer,pipeline
                            tokenizer=AutoTokenizer.from_pretrained(self.settings.hf_safety_model,token=self.settings.hf_token,cache_dir=self.settings.hf_model_cache)
                            model=AutoModelForSequenceClassification.from_pretrained(self.settings.hf_safety_model,token=self.settings.hf_token,cache_dir=self.settings.hf_model_cache)
                            MuRILSafetyProvider._pipeline=pipeline("text-classification",model=model,tokenizer=tokenizer,device=self.settings.model_device)
                result=MuRILSafetyProvider._pipeline(text[:4000],top_k=2);rows=result[0] if result and isinstance(result[0],list) else result;best=max(rows,key=lambda item:item["score"]);label=str(best["label"]).lower()
                mapped="toxic" if label in {"abusive","label_1"} else "normal" if label in {"normal","label_0"} else None
                if not mapped:raise ValueError(f"Unsupported safety label from model: {label}")
                MuRILSafetyProvider._last_active="local_indic_muril";MuRILSafetyProvider._last_error=None
                return SafetyPrediction(mapped,float(best["score"]),[f"Indic MuRIL safety label: {label}"],self.settings.hf_safety_model)
            except Exception as exc:
                MuRILSafetyProvider._last_error=str(exc)
                if provider=="local":raise
        MuRILSafetyProvider._last_active="heuristic_fallback"
        return SafetyPrediction(heuristic_label,heuristic_score,heuristic_evidence,"safety-heuristic-fallback")

def interests(text:str,signals:dict[str,str])->tuple[list[str],list[str]]:
    lowered=text.lower();found=[];evidence=[]
    for label,words in INTERESTS.items():
        matches=sorted(word for word in words if word in lowered)
        if matches:found.append(label);evidence.extend(matches[:2])
    community=signals.get("community")
    if community:found.append(f"Community: {community}");evidence.append(f"public community metadata: {community}")
    return found[:5],evidence[:8]

def influence(engagement:dict[str,int])->tuple[float,list[str]]:
    likes=max(0,engagement.get("likes",0));replies=max(0,engagement.get("replies",0));shares=max(0,engagement.get("shares",0));score=min(100,round(12*math.log1p(likes)+18*math.log1p(replies)+24*math.log1p(shares),2));return score,[f"likes={likes}",f"replies={replies}",f"shares={shares}"]

class CommentIntelligenceService:
    def __init__(self,settings:Settings|None=None):self.sentiment=MuRILSentimentProvider(settings);self.safety=MuRILSafetyProvider(settings);self.csqe=CSQEService()
    def analyse(self,item:CommentInput)->CommentIntelligence:
        prediction=self.sentiment.predict(item.text);language,lang_conf,lang_ev=detect_language(item.text);stance,stance_conf,stance_ev=classify_stance(item.text,item.context);safety_prediction=self.safety.predict(item.text);safety,safety_conf,safety_ev=safety_prediction.label,safety_prediction.score,safety_prediction.evidence;interest_labels,interest_ev=interests(item.text,item.public_signals);influence_score,influence_ev=influence(item.engagement);signal=self.csqe.qualify(item.text)
        geography=item.public_signals.get("location") or None;age=item.public_signals.get("age_bracket") or None
        return CommentIntelligence(sentiment=prediction.label,sentiment_score=prediction.score,stance=stance,emotion="support" if stance=="supportive" else "concern" if stance=="opposing" else "questioning" if stance=="questioning" else "uncertain",safety=safety,language=language,interests=interest_labels,geography=geography,age_bracket=age,influence_score=influence_score,confidence={"sentiment":round(prediction.score,3),"language":lang_conf,"stance":stance_conf,"safety":safety_conf,"geography":.88 if geography else 0,"age":.75 if age else 0,"interests":min(.9,.45+.1*len(interest_labels)),"influence":.9,"signal_quality":signal.signal_quality},evidence={"language":lang_ev,"stance":stance_ev,"safety":safety_ev,"interests":interest_ev,"influence":influence_ev,"geography":["public profile/record metadata"] if geography else ["not inferred without explicit public evidence"],"age":["explicit broad age metadata"] if age else ["not inferred from writing style"],"signal_quality":[signal.reason]},model_name=prediction.model,safety_model_name=safety_prediction.model,signal_quality=signal.signal_quality,signal_classification=signal.classification)

def model_status(settings:Settings|None=None)->dict:
    config=settings or get_settings();local_runtime=bool(importlib.util.find_spec("transformers") and importlib.util.find_spec("torch"))
    if MuRILSentimentProvider._last_active!="not_loaded":active=MuRILSentimentProvider._last_active
    elif config.sentiment_provider=="heuristic":active="heuristic_fallback"
    elif config.sentiment_provider=="endpoint" and not config.hf_inference_endpoint_url:active="unavailable"
    elif config.sentiment_provider=="local" and not local_runtime:active="unavailable"
    else:active="not_loaded"
    safety_active=MuRILSafetyProvider._last_active if MuRILSafetyProvider._last_active!="not_loaded" else "not_loaded" if config.safety_provider!="heuristic" else "heuristic_fallback"
    return {"sentiment":{"requested_provider":config.sentiment_provider,"active_provider":active,"model":config.hf_sentiment_model,"local_runtime_installed":local_runtime,"endpoint_configured":bool(config.hf_inference_endpoint_url),"last_error":MuRILSentimentProvider._last_error,"model_card_note":"This model is not deployed by a shared Hugging Face Inference Provider; use local runtime or a dedicated endpoint."},"safety":{"active_provider":safety_active,"model":config.hf_safety_model,"last_error":MuRILSafetyProvider._last_error,"note":"The Indic model detects abusive content; the narrower hate label additionally requires explicit hate-target evidence. Safety remains separate from sentiment and stance."}}
