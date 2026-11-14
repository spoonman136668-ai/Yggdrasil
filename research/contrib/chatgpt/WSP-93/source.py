"""WSP93 one-shot SQuAD 1.1 corpus capture with official SHA256 pinning.

This file alone may fetch the public SQuAD train/dev downloads. The derived
data file contains only question, passage and source metadata; all answer
labels live in a separate frozen file that scorer only consults after output
freezing. CC BY-SA 4.0 data, with publisher and contributor attribution.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import pathlib
import urllib.parse
import urllib.request

HERE=pathlib.Path(__file__).resolve().parent
SPEC=HERE/"prereg.json"
CORPUS=HERE/"data"/"binding-contexts-frozen.json"
LABELS=HERE/"data"/"binding-labels-frozen.json"
LICENCE="CC BY-SA 4.0"

def canonical(v:object)->bytes:
    return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=True,
                      allow_nan=False).encode("ascii")

def sha(v:object)->str:
    return hashlib.sha256(canonical(v)).hexdigest()

def article_hash(split:str,title:str)->str:
    return hashlib.sha256(("WSP93/"+split+"/"+title).encode("utf-8")).hexdigest()

def question_hash(id:str)->str:
    return hashlib.sha256(("WSP93/qa/"+id).encode("ascii")).hexdigest()

def fetch(name:str,cfg:dict)->dict:
    url=cfg["original_url"]
    limit=cfg["max_download_bytes"]
    req=urllib.request.Request(url,headers={
        "User-Agent":"WSP93YggdrasilResearch/0.1 (+https://github.com/spoonman136668-ai/Yggdrasil)",
        "Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=90) as resp:
        if resp.status!=200:
            raise RuntimeError("official SQuAD HTTP response "+str(resp.status))
        raw=resp.read(limit+1)
    if len(raw)>limit:
        raise ValueError("oversized raw SQuAD source")
    got=hashlib.sha256(raw).hexdigest()
    if got!=cfg["original_raw_sha256"]:
        raise ValueError("raw official SQuAD source SHA256 mismatch")
    parsed=json.loads(raw)
    if parsed.get("version")!="1.1" or not isinstance(parsed.get("data"),list):
        raise ValueError("unexpected SQuAD v1.1 root")
    return {"split":name,"sha256":got,"bytes":len(raw),"data":parsed["data"]}

def eligible_by_title(raw:dict)->dict[str,list[dict]]:
    by_title={}
    qids=set()
    for article in raw["data"]:
        title=article.get("title")
        if not isinstance(title,str) or title in by_title:
            raise ValueError("invalid/duplicate article title")
        questions=[]
        for paragraph in article.get("paragraphs",[]):
            text=paragraph.get("context")
            if not isinstance(text,str) or not(60<=len(text)<=1900):
                continue
            for qa in paragraph.get("qas",[]):
                q=qa.get("question")
                qid=qa.get("id")
                answer_list=qa.get("answers")
                if (not isinstance(qid,str) or not isinstance(q,str) or
                    not (8<=len(q)<=350) or
                    not isinstance(answer_list,list) or not answer_list):
                    continue
                ans=answer_list[0]
                if not isinstance(ans,dict):
                    continue
                a=ans.get("answer_start");v=ans.get("text")
                if (type(a) is not int or not isinstance(v,str) or
                    not(1<=len(v)<=55) or not(0<=a<a+len(v)<=len(text)) or
                    text[a:a+len(v)]!=v):
                    continue
                if qid in qids:
                    raise ValueError("duplicate QA ID in official source split")
                qids.add(qid)
                questions.append({"id":qid,"title":title,"question":q,"context":text,
                                  "answer_start":a,"answer_text":v})
        by_title[title]=sorted(questions,key=lambda q:(question_hash(q["id"]),q["id"]))
    return by_title

def select(raw:dict,count_articles:int,count_each:int,offset:int)->list[dict]:
    groups=eligible_by_title(raw)
    valid=sorted((t for t,q in groups.items() if len(q)>=max(8,count_each)),
                 key=lambda t:(article_hash(raw["split"],t),t))
    titles=valid[offset:offset+count_articles]
    if len(titles)!=count_articles:
        raise ValueError("too few eligible article titles for frozen cohort")
    out=[q for title in titles for q in groups[title][:count_each]]
    if len(out)!=count_articles*count_each:
        raise ValueError("failed exact frozen article x QA count")
    return out

def capture()->dict:
    if CORPUS.exists() or LABELS.exists():
        raise FileExistsError("SQuAD derived source was already frozen; refusing overwrite")
    cfg=json.loads(SPEC.read_text(encoding="utf-8"))["source"]
    train=fetch("train",cfg)
    splits=cfg["cohorts"]
    training=select(train,splits["train_articles"],6,16)
    public=select(train,splits["public_articles"],4,28)
    reserved=select(train,splits["reserved_articles"],4,34)
    if len({z["id"] for z in training+public+reserved})!=len(training+public+reserved):
        raise ValueError("QA ID collision")
    titles=[{x["title"] for x in cohort} for cohort in (training,public,reserved)]
    if titles[0]&titles[1] or titles[0]&titles[2] or titles[1]&titles[2]:
        raise ValueError("article-disjoint dataset invariant failed")
    records=[]
    label_records=[]
    for cohort,rows in (("training",training),("public",public),("reserved",reserved)):
        for row in rows:
            qid=row["id"];text=row["context"]
            url="https://en.wikipedia.org/wiki/"+urllib.parse.quote(
                row["title"].replace(" ","_"))
            records.append({
                "cohort":cohort,"qa_id":qid,"article_title":row["title"],
                "question":row["question"],"context":text,
                "context_sha256":hashlib.sha256(text.encode("utf-8")).hexdigest(),
                "article_url":url,"wikipedia_contributors_url":
                    "https://en.wikipedia.org/w/index.php?title="+urllib.parse.quote(
                    row["title"].replace(" ","_"))+"&action=history",
                "source_dataset":"Stanford Question Answering Dataset v1.1",
                "source_publisher":"Rajpurkar et al. (2016) SQuAD; Wikipedia contributors",
                "license":LICENCE,
            })
            label_records.append({
                "cohort":cohort,"qa_id":qid,
                "answer_text":row["answer_text"],
                "answer_start":row["answer_start"],
            })
    records.sort(key=lambda x:(x["cohort"],x["qa_id"]))
    label_records.sort(key=lambda x:(x["cohort"],x["qa_id"]))
    now=dt.datetime.now(dt.timezone.utc).isoformat()
    header={
        "attribution":"Rajpurkar, Zhang, Lopyrev, Liang 2016, SQuAD v1.1, Wikipedia contributors",
        "citation_url":"https://aclanthology.org/D16-1264/",
        "license":LICENCE,"license_url":"https://creativecommons.org/licenses/by-sa/4.0/",
        "notice":"Derived Wikipedia passage and crowdsourced QA text under CC BY-SA 4.0; retain attribution and share-alike. Selected article URLs link to current pages; text is the exact SQuAD snapshot, NOT a claim about current live Wikipedia article revisions.",
        "captured_utc":now,
        "official_source_sha256":cfg["original_raw_sha256"],
        "selection":"WSP93 uses SQuAD train article ranks 16..41 after the WSP92 training titles; no outcome-based substitution",
        "sampling":splits,
    }
    corpus={"schema":"wsp93.squad1.1-bindings-source-text.v1",
            **header,"records":records,"records_sha256":sha(records)}
    labels={"schema":"wsp93.squad1.1-bindings-source-labels.v1",
            "captured_utc":now,"source_records_sha256":sha(records),
            "license":LICENCE,"labels":label_records,
            "labels_sha256":sha(label_records)}
    CORPUS.parent.mkdir(parents=True,exist_ok=True)
    CORPUS.write_bytes(json.dumps(corpus,sort_keys=True,indent=2,
                                  ensure_ascii=True).encode("ascii")+b"\n")
    LABELS.write_bytes(json.dumps(labels,sort_keys=True,indent=2,
                                  ensure_ascii=True).encode("ascii")+b"\n")
    return {
        "raw_sha256":cfg["original_raw_sha256"],
        "source_records_sha256":corpus["records_sha256"],
        "labels_sha256":labels["labels_sha256"],
        "corpus_file_sha256":hashlib.sha256(CORPUS.read_bytes()).hexdigest(),
        "labels_file_sha256":hashlib.sha256(LABELS.read_bytes()).hexdigest(),
        "record_counts":{c:sum(x["cohort"]==c for x in records)
                         for c in ("training","public","reserved")},
        "titles_by_cohort":{c:len({x["article_title"] for x in records if x["cohort"]==c})
                            for c in ("training","public","reserved")},
    }

def verify()->dict:
    cfg=json.loads(SPEC.read_text(encoding="utf-8"))["source"]
    d=json.loads(CORPUS.read_text(encoding="utf-8"))
    a=json.loads(LABELS.read_text(encoding="utf-8"))
    if (d.get("schema")!="wsp93.squad1.1-bindings-source-text.v1" or
        a.get("schema")!="wsp93.squad1.1-bindings-source-labels.v1" or
        d.get("license")!=LICENCE or a.get("license")!=LICENCE or
        d.get("official_source_sha256")!=cfg["original_raw_sha256"]):
        raise ValueError("source schema/rights/source hash mismatch")
    rows=d.get("records")
    lab=a.get("labels")
    if not isinstance(rows,list) or not isinstance(lab,list):
        raise ValueError("bad records and labels")
    if sha(rows)!=d.get("records_sha256") or sha(lab)!=a.get("labels_sha256") or (
            d["records_sha256"]!=a.get("source_records_sha256")):
        raise ValueError("source/labels canonical hashes do not match")
    byid={x["qa_id"]:x for x in rows}
    if len(byid)!=len(rows) or len(lab)!=len(rows):
        raise ValueError("duplicate or missing source row")
    expected=cfg["cohorts"]
    desired={"training":expected["train_questions"],"public":expected["public_questions"],
             "reserved":expected["reserved_questions"]}
    for cohort,n in desired.items():
        rs=[x for x in rows if x["cohort"]==cohort]
        if len(rs)!=n:
            raise ValueError("unexpected cohort size")
        titles={x["article_title"] for x in rs}
        if len(titles)!=expected[{"training":"train_articles","public":"public_articles","reserved":"reserved_articles"}[cohort]]:
            raise ValueError("unexpected article count")
    titles=[{x["article_title"] for x in rows if x["cohort"]==c}
            for c in ("training","public","reserved")]
    if titles[0]&titles[1] or titles[0]&titles[2] or titles[1]&titles[2]:
        raise ValueError("source leakage across article split")
    for row in rows:
        if (any(k in row for k in ("answer_text","answer_start","answers")) or
            hashlib.sha256(row["context"].encode("utf-8")).hexdigest()!=row["context_sha256"]
            or row.get("license")!=LICENCE):
            raise ValueError("labels present in source or context hash mismatch")
    for y in lab:
        x=byid.get(y["qa_id"])
        if x is None or x["cohort"]!=y["cohort"] or (
                x["context"][y["answer_start"]:y["answer_start"]+len(y["answer_text"])]
                !=y["answer_text"]):
            raise ValueError("annotation-source alignment broken")
    return {
        "source_records_sha256":d["records_sha256"],
        "labels_sha256":a["labels_sha256"],
        "rows":len(rows),"cohorts":desired,
        "corpus_file_sha256":hashlib.sha256(CORPUS.read_bytes()).hexdigest(),
        "labels_file_sha256":hashlib.sha256(LABELS.read_bytes()).hexdigest(),
    }

def main():
    p=argparse.ArgumentParser()
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--capture-once",action="store_true")
    g.add_argument("--verify",action="store_true")
    opts=p.parse_args()
    print("WSP93_SOURCE_RECEIPT="+json.dumps(
        capture() if opts.capture_once else verify(),sort_keys=True),flush=True)

if __name__=="__main__":
    main()
