### IMPORTS ####################################################################

### flask ###

from flask import Flask, render_template, request, redirect, url_for, flash

### FLASK SETUP  ####################################################################
app = Flask(__name__, static_folder='static',static_url_path='/static')
app.config['DEBUG'] = True
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

### APP VIEWS ####################################################################

@app.route("/",methods=['GET','POST'])

def main():
	return render_template('main.html')
	

### RUN IT ####################################################################

if __name__ == '__main__': # If we're executing this app from the command line
    #app.run("127.0.0.1", port = 3000, debug=True, use_reloader=False)
    app.run(debug=True, use_reloader=False)