import os

os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
import torch
from flask import Flask, request, render_template
from flask_cors import CORS, cross_origin
from transformers import BertModel, BertConfig, BertTokenizer, FlaxBertForQuestionAnswering, pipeline
import gensim
from transformers import logging
import json

logging.set_verbosity_error()

DATASET_PATH = '~/Downloads/GoogleNews-vectors-negative300.bin'

# Initializing a BERT bert-base-uncased style configuration
configuration = BertConfig()

# Initializing a model from the bert-base-uncased style configuration
model = BertModel(configuration)

# Accessing the model configuration
configuration = model.config
app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('fourBlanks.html')


@app.post('/search')
def search():
    result = {}
    sentence = "{A} is to {B} as {C} is to {D}."
    return render_template('fourBlanks.html',
                           result=fillMaskWithModels(sentence, ['bert-base-uncased', 'roberta-base', 'roberta-large', 'vocab-transformers/distilbert-word2vec_256k-MLM_1M', 'gensim']))

@app.post('/search2')
def search2():
    data = request.get_json(silent=True)
    result = {}
    content = request.get_json(force=True)
    print(content)
    sentence = "{A} is to {B} as {C} is to {D}."
    return fillMaskWithModels(content, sentence, ['bert-base-uncased', 'roberta-base', 'roberta-large', 'vocab-transformers/distilbert-word2vec_256k-MLM_1M', 'gensim'])


def findIndexHF(result, target):
    for index, item in enumerate(result):
        if item['token_str'] == target.lower():
            return index
    return None
def findIndexAndTrueScore(gensimResult, target):
    for index, item in enumerate(gensimResult):
        if item[0] == target:
            return index, item[1]
    return None, 0


def searchLocalJson(formA, formB, formC, formD):
    res = {'B': [], 'D': []}
    with open('resultB.json', 'r') as openfile:
        # Reading from json file
        items = json.load(openfile)
        for item in items:
            if item['A'] == formA and item['C'] == formC and item['D'] == formD:
                # item found, return item['Data']
                res['B'] = item['Data']
    with open('resultD.json', 'r') as openfile:
        # Reading from json file
        items = json.load(openfile)
        for item in items:
            if item['A'] == formA and item['C'] == formC and item['B'] == formB:
                # item found, return item['Data']
                res['D'] = item['Data']
    print(res)
    return res

def saveLocalJson(formA, formB, formC, formD, result):
    with open("resultB.json", 'r+') as file:
        # First we load existing data into a dict.
        file_data = json.load(file)
        # Join new_data with file_data inside emp_details
        file_data.append({"A": formA, "C": formC, "D": formD, "Data": result["B"]})
        # Sets file's current position at offset.
        file.seek(0)
        # convert back to json.
        json.dump(file_data, file, indent=4)
    with open("resultD.json", 'r+') as file:
        # First we load existing data into a dict.
        file_data = json.load(file)
        # Join new_data with file_data inside emp_details
        file_data.append({"A": formA, "B": formB, "C": formC, "Data": result["D"]})
        # Sets file's current position at offset.
        file.seek(0)
        # convert back to json.
        json.dump(file_data, file, indent=4)

@cross_origin()
def fillMaskWithModels(content, sentence, models):
    result = {'B': [], 'D': []}  # {B: [{}, {}, {}], D:[{}, {}, {}]}
    formA = content.get('formA')
    formB = content.get('formB')
    formC = content.get('formC')
    formD = content.get('formD')
    print(formA, formB, formC, formD)
    localRes = searchLocalJson(formA, formB, formC, formD)
    if localRes['B'] != [] and localRes['D'] != []:
        return localRes
    for model in models:
        mask = 'NoneNone'
        if model == 'gensim':
            gensimD, gensimB = gensimWord2Vec(formA, formB, formC, formD)
            topD, topDScore = gensimD[0]
            trueD = formD
            trueDIdx, trueDScore = findIndexAndTrueScore(gensimD, trueD)
            reciprocalRank = 1.0 / (trueDIdx + 1) if trueDIdx is not None else 'NA'
            result['D'].append({'model': model, 'topD': topD, 'topDScore': topDScore, 'topDRank': 1.0,
                                'topDSentence': sentence.format(A=formA, B=formB, C=formC, D='*' + topD), 'trueD': trueD,
                                'trueDScore': trueDScore,
                                'trueDRank': reciprocalRank, 'trueDSentence': sentence.format(A=formA, B=formB, C=formC, D='*' + formD)})
            topB, topBScore = gensimB[0]
            trueB = formB
            trueBIdx, trueBScore = findIndexAndTrueScore(gensimB, formB)
            reciprocalRank = 1.0 / (trueBIdx + 1) if trueBIdx is not None else 'NA'
            result['B'].append({'model': model, 'topD': topB, 'topDScore': topBScore, 'topDRank': 1.0,
                                'topDSentence': sentence.format(A=formA, B='*' + topB, C=formC, D=formD), 'trueD': trueB,
                                'trueDScore': trueBScore,
                                'trueDRank': reciprocalRank, 'trueDSentence': sentence.format(A=formA, B='*' + formB, C=formC, D=formD)})
            continue
        elif model == 'bert-base-uncased' or model == 'vocab-transformers/distilbert-word2vec_256k-MLM_1M':
            mask = '[MASK]'
        elif model == 'roberta-base' or model == 'roberta-large':
            mask = '<mask>'
        tmp1 = sentence.format(A=formA, B=formB, C=formC, D=mask)
        tmp2 = sentence.format(A=formA, B=mask, C=formC, D=formD)
        unmasker = pipeline('fill-mask', model=model, top_k=2000, device=torch.device("mps"))
        if mask in tmp1:
            tmp1result = unmasker(tmp1)
            topD, topDScore = tmp1result[0]['token_str'], tmp1result[0]['score']
            trueD, trueDScore = formD, unmasker(tmp1, targets=formD)[0]['score']
            if model.startswith('roberta'):
                trueDScore = max(trueDScore, unmasker(tmp1, targets=" " + formD)[0]['score'], unmasker(tmp1, targets=formD + " ")[0]['score'])
            idx = findIndexHF(tmp1result, formD)
            reciprocalRank = 1.0 / (idx + 1) if idx is not None else 'NA'
            result['D'].append({'model': model, 'topD': topD, 'topDScore': topDScore, 'topDRank': 1.0,
                                 'topDSentence': tmp1.replace(mask, "*" + topD), 'trueD': trueD,
                                 'trueDScore': trueDScore,
                                 'trueDRank': reciprocalRank, 'trueDSentence': tmp1.replace(mask, "*" + trueD)})
        if mask in tmp2:
            tmp2result = unmasker(tmp2)
            topB, topBScore = tmp2result[0]['token_str'], tmp2result[0]['score'],
            trueB, trueBScore = formB, unmasker(tmp2, targets=formB)[0]['score']
            if model.startswith('roberta'):
                trueBScore = max(trueDScore, unmasker(tmp1, targets=" " + formB)[0]['score'],
                                 unmasker(tmp1, targets=formB + " ")[0]['score'])
            idx = findIndexHF(tmp2result, formB)
            reciprocalRank = 1.0 / (idx + 1) if idx is not None else 'NA'
            result['B'].append({'model': model, 'topD': topB, 'topDScore': topBScore, 'topDRank': 1.0,
                                 'topDSentence': tmp2.replace(mask, "*" + topB), 'trueD': trueB,
                                 'trueDScore': trueBScore,
                                 'trueDRank': reciprocalRank, 'trueDSentence': tmp2.replace(mask, "*" + trueB)})
    saveLocalJson(formA, formB, formC, formD, result)
    return result


def printConfig():
    print(f"PyTorch version: {torch.__version__}")

    # Check PyTorch has access to MPS (Metal Performance Shader, Apple's GPU architecture)
    print(f"Is MPS (Metal Performance Shader) built? {torch.backends.mps.is_built()}")
    print(f"Is MPS available? {torch.backends.mps.is_available()}")

    # Set the device
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    print(f"Using device: {device}")

def gensimWord2Vec(formA, formB, formC, formD):
    wv = gensim.models.KeyedVectors.load_word2vec_format(DATASET_PATH, binary=True)
    gensimD = wv.most_similar(positive=[formA, formC], negative=[formB], topn=2000)
    gensimB = wv.most_similar(positive=[formA, formC], negative=[formD], topn=2000)
    return gensimD, gensimB


if __name__ == '__main__':
    printConfig()
    app.run(port=8888)
