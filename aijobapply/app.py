import json
import logging

from flask import Flask, flash, redirect, render_template, request, url_for

from aijobapply.main import run_application

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a real secret key for production

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        form_data = request.form.to_dict()
        try:
            run_application(form_data)
            flash("AIJobApply has been successfully executed.", "success")
        except Exception as e:
            logging.exception(e)
            flash(f"Error running AIJobApply: {e}", "error")
        return redirect(url_for('index'))

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
