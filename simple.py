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
    return render_template('search.html')

@app.post('/search')
def search():
    s = request.form['sentence']
    unmasker = pipeline('fill-mask', model='bert-base-uncased')
    tmp = s.replace("_", "[MASK]")
    if '[MASK]' in tmp:
        res = unmasker(tmp)
        return render_template('search.html', res=tmp.replace('[MASK]', res[0]['token_str']))
    else:
        return render_template('search.html')

if __name__=='__main__':
   app.run(port=8888)