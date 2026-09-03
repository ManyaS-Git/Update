from __future__ import annotations
import asyncio,csv,json,math
from collections import Counter,defaultdict
from datetime import datetime,timezone
from pathlib import Path
from sqlalchemy import func,select
from app.core.config import get_settings
from app.models.database import FeedbackRecord,SessionLocal,SourceCommentRecord,StoryRecord,TrainingLabelRecord

ROOT=Path(__file__).resolve().parents[2]
RAW=ROOT/"data/raw"

def _rows(path:Path,text_key:str,label_key:str)->tuple[list[str],list[str]]:
    if not path.exists():return [],[]
    with path.open(encoding="utf-8-sig") as handle:
        rows=list(csv.DictReader(handle))
    return [row[text_key].strip() for row in rows if row.get(text_key) and row.get(label_key)],[row[label_key].strip().lower() for row in rows if row.get(text_key) and row.get(label_key)]

def _dedupe(texts:list[str],labels:list[str])->tuple[list[str],list[str]]:
    clean={}
    for text,label in zip(texts,labels):
        key=" ".join(text.lower().split())
        if key and (key not in clean or clean[key][1]==label):clean[key]=(text,label)
    return [value[0] for value in clean.values()],[value[1] for value in clean.values()]

def _pipeline(kind:str="char",c:float=2):
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import Pipeline
    vector=TfidfVectorizer(analyzer="char_wb",ngram_range=(3,5),min_df=2,max_features=60000,sublinear_tf=True) if kind=="char" else TfidfVectorizer(ngram_range=(1,2),min_df=2,max_features=50000,sublinear_tf=True)
    return Pipeline([("features",vector),("classifier",LogisticRegression(C=c,max_iter=1200,class_weight="balanced"))])

def _evaluate_candidates(train_x,train_y,test_x,test_y)->tuple[object,dict]:
    from sklearn.dummy import DummyClassifier
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics import accuracy_score,classification_report,f1_score
    from sklearn.pipeline import Pipeline
    candidates={"word_c2":_pipeline("word",2),"char_c1":_pipeline("char",1),"char_c3":_pipeline("char",3)}
    dummy=Pipeline([("features",TfidfVectorizer()),("classifier",DummyClassifier(strategy="most_frequent"))]);dummy.fit(train_x,train_y);baseline=f1_score(test_y,dummy.predict(test_x),average="macro",zero_division=0)
    best=None;best_report=None
    for name,model in candidates.items():
        model.fit(train_x,train_y);pred=model.predict(test_x);macro=f1_score(test_y,pred,average="macro",zero_division=0);report={"candidate":name,"macro_f1":round(macro,4),"accuracy":round(accuracy_score(test_y,pred),4),"per_class":classification_report(test_y,pred,output_dict=True,zero_division=0)}
        if best_report is None or macro>best_report["macro_f1"]:best,best_report=model,report
    best_report["baseline_macro_f1"]=round(baseline,4);best_report["accepted"]=best_report["macro_f1"]>=baseline+.05
    return best,best_report

def train_supervised()->dict:
    from joblib import dump
    from sklearn.model_selection import train_test_split
    settings=get_settings();target=Path(settings.trained_model_dir);target.mkdir(parents=True,exist_ok=True);results={}
    texts,labels=_rows(RAW/"hinglish_sentiment.csv","tweet","sentiment");hindi_texts,hindi_labels=_rows(RAW/"sentihin_2500.csv","sentence","sentiment");texts.extend(hindi_texts);labels.extend(hindi_labels)
    with SessionLocal() as db:
        reviewed=db.scalars(select(TrainingLabelRecord).where(TrainingLabelRecord.sentiment.is_not(None))).all()
    texts.extend(row.text for row in reviewed);labels.extend(row.sentiment for row in reviewed if row.sentiment);texts,labels=_dedupe(texts,labels)
    if len(texts)>=settings.learning_min_labels and len(set(labels))>1:
        train_x,test_x,train_y,test_y=train_test_split(texts,labels,test_size=.25,random_state=42,stratify=labels);model,report=_evaluate_candidates(train_x,train_y,test_x,test_y);report.update({"task":"sentiment","train_examples":len(train_x),"test_examples":len(test_x)})
        if report["accepted"]:dump(model,target/"sentiment.joblib")
        elif (target/"sentiment.joblib").exists():(target/"sentiment.joblib").unlink()
        results["sentiment"]=report
    else:
        if (target/"sentiment.joblib").exists():(target/"sentiment.joblib").unlink()
        results["sentiment"]={"status":"insufficient_unique_labels","examples":len(texts),"minimum":settings.learning_min_labels}
    train_x,train_y=_rows(RAW/"prism_hate_train.csv","text","label");val_x,val_y=_rows(RAW/"prism_hate_val.csv","text","label");test_x,test_y=_rows(RAW/"prism_hate_test.csv","text","label")
    if train_x and test_x:
        model,report=_evaluate_candidates(train_x+val_x,train_y+val_y,test_x,test_y);report.update({"task":"safety_binary","train_examples":len(train_x)+len(val_x),"test_examples":len(test_x),"label_note":"PRISM binary task; production hate-vs-toxic policy remains separate"})
        if report["accepted"]:dump(model,target/"safety_binary.joblib")
        results["safety_binary"]=report
    return results

def train_topics()->dict:
    from joblib import dump
    from sklearn.cluster import MiniBatchKMeans
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics import silhouette_score
    settings=get_settings();target=Path(settings.trained_model_dir);target.mkdir(parents=True,exist_ok=True)
    with SessionLocal() as db:texts=list(db.scalars(select(SourceCommentRecord.text)).all())+list(db.scalars(select(StoryRecord.title)).all())
    texts=list(dict.fromkeys(text for text in texts if len(text.split())>=3))
    if len(texts)<60:
        if (target/"topics.joblib").exists():(target/"topics.joblib").unlink()
        return {"status":"insufficient_data","examples":len(texts),"minimum":60}
    vector=TfidfVectorizer(ngram_range=(1,2),min_df=2,max_features=20000,sublinear_tf=True);matrix=vector.fit_transform(texts);best=None
    for k in (4,6,8):
        if len(texts)<=k:continue
        model=MiniBatchKMeans(n_clusters=k,random_state=42,n_init=10,batch_size=256).fit(matrix);sample=min(2000,len(texts));score=silhouette_score(matrix[:sample],model.labels_[:sample])
        if best is None or score>best[0]:best=(score,model)
    score,model=best;terms=vector.get_feature_names_out();clusters={str(i):[str(terms[index]) for index in model.cluster_centers_[i].argsort()[-8:][::-1]] for i in range(model.n_clusters)};accepted=score>=.08
    if accepted:dump({"vectorizer":vector,"model":model},target/"topics.joblib")
    elif (target/"topics.joblib").exists():(target/"topics.joblib").unlink()
    return {"status":"trained" if accepted else "rejected_low_separation","accepted":accepted,"examples":len(texts),"clusters":clusters if accepted else {},"silhouette":round(float(score),4),"minimum_silhouette":.08}

def train_feedback_policy()->dict:
    settings=get_settings();target=Path(settings.trained_model_dir);target.mkdir(parents=True,exist_ok=True)
    with SessionLocal() as db:rows=db.scalars(select(FeedbackRecord)).all()
    grouped=defaultdict(list)
    for row in rows:grouped[(row.context,row.action)].append(row.reward)
    contexts={}
    for (context,action),rewards in grouped.items():
        contexts.setdefault(context,{})[action]={"uses":len(rewards),"mean_reward":round(sum(rewards)/len(rewards),4),"ucb":round(sum(rewards)/len(rewards)+math.sqrt(2*math.log(max(2,len(rows)))/len(rewards)),4)}
    policy={context:max(actions,key=lambda action:actions[action]["ucb"]) for context,actions in contexts.items()};report={"status":"trained" if len(rows)>=20 else "collecting_feedback","events":len(rows),"minimum":20,"policy":policy,"actions":contexts};(target/"feedback_policy.json").write_text(json.dumps(report,indent=2),encoding="utf-8");return report

def train_all()->dict:
    started=datetime.now(timezone.utc);report={"started_at":started.isoformat(),"training_signature":training_signature(),"supervised":train_supervised(),"unsupervised":train_topics(),"reinforcement_feedback":train_feedback_policy()};report["completed_at"]=datetime.now(timezone.utc).isoformat();target=Path(get_settings().trained_model_dir);target.mkdir(parents=True,exist_ok=True);(target/"latest_report.json").write_text(json.dumps(report,indent=2),encoding="utf-8");return report

def training_signature()->dict:
    with SessionLocal() as db:return {"human_labels":db.scalar(select(func.count(TrainingLabelRecord.id))) or 0,"feedback_events":db.scalar(select(func.count(FeedbackRecord.id))) or 0,"collected_comments":db.scalar(select(func.count(SourceCommentRecord.id))) or 0,"stories":db.scalar(select(func.count(StoryRecord.id))) or 0}

def learning_status()->dict:
    target=Path(get_settings().trained_model_dir);report=target/"latest_report.json"
    with SessionLocal() as db:counts={"human_labels":db.scalar(select(func.count(TrainingLabelRecord.id))) or 0,"feedback_events":db.scalar(select(func.count(FeedbackRecord.id))) or 0,"collected_comments":db.scalar(select(func.count(SourceCommentRecord.id))) or 0}
    return {"counts":counts,"latest_report":json.loads(report.read_text()) if report.exists() else None,"artifacts":sorted(path.name for path in target.glob("*") if path.is_file()) if target.exists() else []}

async def continuous_learning_loop()->None:
    settings=get_settings();await asyncio.sleep(60)
    while True:
        try:
            status=learning_status();previous=(status.get("latest_report") or {}).get("training_signature")
            if training_signature()!=previous:await asyncio.to_thread(train_all)
        except Exception:pass
        await asyncio.sleep(max(300,settings.continuous_learning_interval_minutes*60))
