import os

os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
import torch
from flask import Flask, request, render_template
from transformers import BertModel, BertConfig, BertTokenizer, FlaxBertForQuestionAnswering, pipeline

# Initializing a BERT bert-base-uncased style configuration
configuration = BertConfig()

# Initializing a model from the bert-base-uncased style configuration
model = BertModel(configuration)

# Accessing the model configuration
configuration = model.config
app = Flask(__name__)


@app.route('/')
def index():
    return render_template('fourBlanks.html')


@app.post('/search')
def search():
    result = {}
    sentence = "{A} is to {B} as {C} is to {D}."
    return render_template('fourBlanks.html',
                           result=fillMaskWithModels(sentence, ['bert-base-uncased', 'roberta-base', 'roberta-large', 'vocab-transformers/distilbert-word2vec_256k-MLM_1M']))


def findIndex(result, target):
    for index, item in enumerate(result):
        if item['token_str'] == target.lower():
            return index
    return None


def fillMaskWithModels(sentence, models):
    result = {'B': [], 'D': []}  # {B: [{}, {}, {}], D:[{}, {}, {}]}
    for model in models:
        mask = 'NoneNone'
        if model == 'bert-base-uncased' or model == 'vocab-transformers/distilbert-word2vec_256k-MLM_1M':
            mask = '[MASK]'
        elif model == 'roberta-base' or model == 'roberta-large':
            mask = '<mask>'
        tmp1 = sentence.format(A=request.form['A'], B=request.form['B'], C=request.form['C'], D=mask)
        tmp2 = sentence.format(A=request.form['A'], B=mask, C=request.form['C'], D=request.form['D'])
        unmasker = pipeline('fill-mask', model=model, top_k=2000, device=torch.device("mps"))
        if mask in tmp1:
            tmp1result = unmasker(tmp1)
            topD, topDScore = tmp1result[0]['token_str'], tmp1result[0]['score']
            trueD, trueDScore = request.form['D'], unmasker(tmp1, targets=request.form['D'])[0]['score']
            idx = findIndex(tmp1result, request.form['D'])
            reciprocalRank = 1.0 / (idx + 1) if idx is not None else 'NA'
            result['D'].append({'model': model, 'topD': topD, 'topDScore': topDScore, 'topDRank': 1.0,
                                 'topDSentence': tmp1.replace(mask, "*" + topD), 'trueD': trueD,
                                 'trueDScore': trueDScore,
                                 'trueDRank': reciprocalRank, 'trueDSentence': tmp1.replace(mask, "*" + trueD)})
            # tmpList.append(
            # model + "'s top prediction: " + tmp1.replace(mask, "*" + topD) + " " + "Score: " + str(topDScore))
            # tmpList.append(
            #     model + "'s score for your answer: " + tmp1.replace(mask, "*" + trueD) + " " + "Score: " + str(
            #         trueDScore) + " " + "Reciprocal Rank: " + str(reciprocalRank))
        if mask in tmp2:
            tmp2result = unmasker(tmp2)
            topB, topBScore = tmp2result[0]['token_str'], tmp2result[0]['score'],
            trueB, trueBScore = request.form['B'], unmasker(tmp2, targets=request.form['B'])[0]['score']
            idx = findIndex(tmp2result, request.form['B'])
            reciprocalRank = 1.0 / (idx + 1) if idx is not None else 'NA'
            result['B'].append({'model': model, 'topD': topB, 'topDScore': topBScore, 'topDRank': 1.0,
                                 'topDSentence': tmp2.replace(mask, "*" + topB), 'trueD': trueB,
                                 'trueDScore': trueBScore,
                                 'trueDRank': reciprocalRank, 'trueDSentence': tmp2.replace(mask, "*" + trueB)})
            # tmpList.append(
            #     model + "'s top prediction: " + tmp2.replace(mask, "*" + topB) + " " + "Score: " + str(topBScore))
            # tmpList.append(
            #     model + "'s score for your answer: " + tmp2.replace(mask, "*" + trueB) + " " + "Score: " + str(
            #         trueBScore) + " " + "Reciprocal Rank: " + str(reciprocalRank))
    return result


def printConfig():
    print(f"PyTorch version: {torch.__version__}")

    # Check PyTorch has access to MPS (Metal Performance Shader, Apple's GPU architecture)
    print(f"Is MPS (Metal Performance Shader) built? {torch.backends.mps.is_built()}")
    print(f"Is MPS available? {torch.backends.mps.is_available()}")

    # Set the device
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    print(f"Using device: {device}")


if __name__ == '__main__':
    printConfig()
    app.run(port=8888)
