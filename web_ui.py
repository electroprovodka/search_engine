from flask import Flask, render_template, url_for, redirect, g
from flask_bootstrap import Bootstrap
from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from indexer import Searcher, InMemoryIndeces, ShelveIndeces
from lang_proc import to_query_terms

app = Flask(__name__)
Bootstrap(app)
# TODO: configurable
searcher = Searcher('shelve_indeces', ShelveIndeces)


#@app.before_first_request
#def init_searcher():
#	g.searcher = Searcher('indeces')

class SearchForm(Form):
	user_query = StringField('user_query', validators=[DataRequired()])
	search_button = SubmitField('Search!')


@app.route("/", methods=['GET', 'POST'])
def index():
	search_form = SearchForm(csrf_enabled=False)
	if search_form.validate_on_submit():
		return redirect(url_for("search_results", query=search_form.user_query.data))
	return render_template('index.html', form=search_form)

@app.route("/search_results/<query>")
def search_results(query):
	query_terms = to_query_terms(query)
	docids = searcher.find_documents_OR(query_terms)
	urls = [searcher.get_url(doc_id) for doc_id in docids]
	texts = [searcher.generate_snippet(query_terms, doc_id) for doc_id in docids]
	return render_template('search_results.html', query=query, urls_and_texts=zip(urls, texts))

if __name__ == '__main__':
	app.run(debug=True)