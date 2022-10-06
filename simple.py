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
                           result=fillMaskWithModels(sentence, ['bert-base-uncased', 'roberta-base']))


def fillMaskWithModels(sentence, models):
    result = []
    for model in models:
        mask = 'NoneNone'
        if model == 'bert-base-uncased':
            mask = '[MASK]'
        elif model == 'roberta-base':
            mask = '<mask>'
        tmp1 = sentence.format(A=request.form['A'], B=request.form['B'], C=request.form['C'], D=mask)
        tmp2 = sentence.format(A=request.form['A'], B=mask, C=request.form['C'], D=request.form['D'])
        tmpList = []
        unmasker = pipeline('fill-mask', model=model, top_k=20)
        if mask in tmp1:
            tmp1result = unmasker(tmp1)
            topD, topDScore = tmp1result[0]['token_str'], tmp1result[0]['score']
            trueD, trueDScore = request.form['D'], unmasker(tmp1, targets=request.form['D'])[0]['score']
            idx = next((index for (index, d) in enumerate(tmp1result) if d["token_str"] == request.form['D']), None)
            reciprocalRank = 1.0 / (idx + 1) if idx != None else 0
            tmpList.append(
                model + "'s top prediction: " + tmp1.replace(mask, "*" + topD) + " " + "Score: " + str(topDScore))
            tmpList.append(
                model + "'s score for your answer: " + tmp1.replace(mask, "*" + trueD) + " " + "Score: " + str(
                    trueDScore) + " " + "Reciprocal Rank: " + str(reciprocalRank))
        if mask in tmp2:
            tmp2result = unmasker(tmp2)
            topB, topBScore = tmp2result[0]['token_str'], tmp2result[0]['score'],
            trueB, trueBScore = request.form['B'], unmasker(tmp2, targets=request.form['B'])[0]['score']
            idx = next((index for (index, d) in enumerate(tmp2result) if d["token_str"] == request.form['B']), None)
            reciprocalRank = 1.0 / (idx + 1) if idx != None else 0
            tmpList.append(
                model + "'s top prediction: " + tmp1.replace(mask, "*" + topB) + " " + "Score: " + str(topBScore))
            tmpList.append(
                model + "'s score for your answer: " + tmp1.replace(mask, "*" + trueB) + " " + "Score: " + str(
                    trueBScore) + " " + "Reciprocal Rank: " + str(reciprocalRank))
        result.append(tmpList)
    return result


if __name__ == '__main__':
    app.run(port=8888)
