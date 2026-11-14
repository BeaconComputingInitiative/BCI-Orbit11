# BEACON COMPUTING INITIATIVE | Orbital Neural Core
# Developer Seal: CJB-DEV-2026
# File SHA-256: SHA256SUMS
"""Dependency-free CPU-native 12→8→3→8→12 neural autoencoder."""
from __future__ import annotations
import copy
import math
import random
import statistics
from .common import FEATURES, MODEL_SCHEMA, HEADER, SEAL, parse_time, validate_window

SIZES = (len(FEATURES),8,3,8,len(FEATURES))


def qtile(values, p):
    x=sorted(values)
    if not x: raise ValueError('no calibration values')
    return x[max(0,min(len(x)-1,math.ceil(p*len(x))-1))]


def initial_weights(seed):
    rng=random.Random(seed)
    layers=[]
    for n_in,n_out in zip(SIZES,SIZES[1:]):
        scale=math.sqrt(2/(n_in+n_out))
        layers.append({'w':[[rng.uniform(-scale,scale) for _ in range(n_in)] for _ in range(n_out)],
                       'b':[0.0]*n_out})
    return layers


def vector(item):
    validate_window(item)
    return [math.log1p(item['features'][k]) for k in FEATURES]


def standardized(v,mu,sigma):
    return [max(-8.,min(8.,(x-m)/s)) for x,m,s in zip(v,mu,sigma)]


def forward(layers,x):
    activations=[x]
    for j,layer in enumerate(layers):
        outputs=[sum(w*v for w,v in zip(row,activations[-1]))+bias
                 for row,bias in zip(layer['w'],layer['b'])]
        if j<len(layers)-1:
            outputs=[math.tanh(max(-25,min(25,y))) for y in outputs]
        activations.append(outputs)
    return activations


def loss_and_contrib(layers,x):
    y=forward(layers,x)[-1]
    parts=[(a-b)**2 for a,b in zip(x,y)]
    return sum(parts)/len(parts),parts


def learn(layers,x,lr):
    acts=forward(layers,x)
    deltas=[None]*len(layers)
    y=acts[-1]
    deltas[-1]=[2*(v-target)/len(x) for v,target in zip(y,x)]
    for i in range(len(layers)-2,-1,-1):
        below=layers[i+1]['w']
        next_d=deltas[i+1]
        a=acts[i+1]
        deltas[i]=[(1-z*z)*sum(below[k][j]*next_d[k] for k in range(len(next_d)))
                   for j,z in enumerate(a)]
    # Compute all gradients before mutating any layer.
    for i,layer in enumerate(layers):
        for j,row in enumerate(layer['w']):
            d=max(-2,min(2,deltas[i][j]))
            for k in range(len(row)):
                row[k]-=lr*(d*acts[i][k]+1e-5*row[k])
            layer['b'][j]-=lr*d


def train(windows,context,approval_sha,seed=440,epochs=90,lr=0.012):
    if not (1<=epochs<=350 and 0<lr<=0.05):
        raise ValueError('training bounds violated')
    selected=sorted((r for r in windows if r['context']==context),key=lambda r:parse_time(r['ts']))
    if len(selected)<80 or len(selected)!=len(windows):
        raise ValueError('at least 80 same-context samples required')
    split=max(64,int(len(selected)*.8))
    train_rows=selected[:split]; valid_rows=selected[split:]
    if len(valid_rows)<16: raise ValueError('at least 16 held-out samples required')
    training=[vector(r) for r in train_rows]
    validation=[vector(r) for r in valid_rows]
    means=[statistics.mean(v[k] for v in training) for k in range(len(FEATURES))]
    stds=[max(.15,statistics.pstdev(v[k] for v in training)) for k in range(len(FEATURES))]
    tr=[standardized(r,means,stds) for r in training]
    va=[standardized(r,means,stds) for r in validation]
    layers=initial_weights(seed)
    rng=random.Random(seed)
    best=float('inf'); best_layers=copy.deepcopy(layers); patience=0
    for epoch in range(epochs):
        order=list(range(len(tr))); rng.shuffle(order)
        for ix in order:
            learn(layers,tr[ix],lr)
        score=statistics.mean(loss_and_contrib(layers,x)[0] for x in va)
        if not math.isfinite(score): raise ValueError('divergent numerical model')
        if score<best-1e-7:
            best=score; best_layers=copy.deepcopy(layers); patience=0
        else:
            patience+=1
        if patience>=22: break
    errors=[loss_and_contrib(best_layers,x)[0] for x in va]
    # Calibrated on held-out *candidate-normal* windows. Not a probability of attack.
    threshold=max(0.015,qtile(errors,.99)*1.3)
    return {
        'header':HEADER,'developer_seal':SEAL,'schema':MODEL_SCHEMA,'model_state':'candidate_unpromoted',
        'context':context,'approval_sha256':approval_sha,'architecture':list(SIZES),
        'features':list(FEATURES),'preprocess':'log1p+train_zscore_clip8',
        'means':means,'stds':stds,'layers':best_layers,'anomaly_threshold':threshold,
        'train_windows':len(tr),'validation_windows':len(va),
        'validation_mse':best,'heldout_p95_mse':qtile(errors,.95),
        'calibrated_candidate_false_positive_rate':sum(e>=threshold for e in errors)/len(errors),
        'seed':seed,'epochs_completed':epoch+1,
        'warning':'Anomaly measures reconstruction novelty, not malware probability or intent; never authorizes containment.'
    }


def validate_model(model):
    if model.get('schema')!=MODEL_SCHEMA or model.get('developer_seal')!=SEAL or model.get('model_state')!='candidate_unpromoted':
        raise ValueError('model schema/state mismatch')
    if tuple(model.get('features',[]))!=FEATURES or tuple(model.get('architecture',[]))!=SIZES:
        raise ValueError('model feature/architecture mismatch')
    if len(model.get('layers',[]))!=len(SIZES)-1:
        raise ValueError('malformed layers')
    for layer,a,b in zip(model['layers'],SIZES,SIZES[1:]):
        if len(layer['w'])!=b or len(layer['b'])!=b:
            raise ValueError('layer dimensions invalid')
        for row in layer['w']:
            if len(row)!=a or any(not isinstance(x,(int,float)) or not math.isfinite(x) for x in row):
                raise ValueError('invalid weights')
        if any(not isinstance(x,(int,float)) or not math.isfinite(x) for x in layer['b']):
            raise ValueError('invalid bias')
    if len(model.get('means',[]))!=len(FEATURES) or len(model.get('stds',[]))!=len(FEATURES):
        raise ValueError('invalid normalization')
    if any(not isinstance(s,(int,float)) or not math.isfinite(s) or s<=0 for s in model['stds']):
        raise ValueError('invalid standard deviations')
    if any(not isinstance(m,(int,float)) or not math.isfinite(m) for m in model['means']):
        raise ValueError('invalid normalization means')
    if not isinstance(model.get('context'),str) or not model['context']:
        raise ValueError('missing model context')
    if not isinstance(model.get('anomaly_threshold'),(float,int)) or not 0<model['anomaly_threshold']<1e9:
        raise ValueError('invalid calibration threshold')
    return True


def score(model,observation):
    validate_model(model)
    validate_window(observation)
    if observation['context']!=model['context']:
        raise ValueError('HOLD: contexts not interchangeable; explicit mapping required')
    z=standardized(vector(observation),model['means'],model['stds'])
    mse,parts=loss_and_contrib(model['layers'],z)
    ordered=sorted(range(len(FEATURES)),key=lambda i:parts[i],reverse=True)
    return {'ts':observation['ts'],'context':observation['context'],'model_state':model['model_state'],
            'anomaly_score_mse':round(mse,6),'threshold':round(model['anomaly_threshold'],6),
            'candidate_anomaly':mse>=model['anomaly_threshold'],
            'top_contributors':[{'feature':FEATURES[i], 'squared_reconstruction_error':round(parts[i],6)}
                                for i in ordered[:4]],
            'trust':observation['trust'],
            'interpretation':'Statistical deviation only; independent evidence required for threat inference.'}
