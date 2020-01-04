from flask import Flask, render_template, flash, request
from wtforms import Form, SelectField, DateField, SubmitField, validators, ValidationError
from flask_wtf import FlaskForm
from datetime import date
from wtforms.validators import DataRequired
import sys
sys.path.append("../whereistheplanet/whereistheplanet/") 
import whereistheplanet

app = Flask(__name__)
app.secret_key = 'development key'

multchoices = [("", 'Choose one'),
               ("hr8799b", "HR 8799 b"), 
               ("hr8799c", "HR 8799 c"), 
               ("hr8799d", "HR 8799 d"), 
               ('hr8799e', "HR 8799 e"), 
               ('betapicb', "bet Pic b"), 
               ('51erib', "51 Eri b"), 
               ('hd206893b',"HD 206893 b"),
               ('1rxs0342+1216b', "1RXS J160929.1-210524 b"), 
               ('1rxs2351+3127b', "1RXS J2351+3127 b"), 
               ('2m1559+4403b', "2MASS 1559+4403 b"), 
               ('cd-352722b', "CD-35 2722 b"), 
               ('dhtaub', "DH Tau b"), 
               ('gj504b', "GJ 504 b"), 
               ('hd984b', "HD 984 b"), 
               ('hd1160b', "HD 1160 b"), 
               ('hd19467b', "HD 19467 b"), 
               ('hd23514b', "HD 23514 b"), 
               ('hd49197b', "HD 49197 b"), 
               ('hd95086b', "HD 95086 b"), 
               ('hip65426b', "HIP 65426 b"), 
               ('hr2562b', "HR 2562 b"), 
               ('hr3549b', "HR 3549 b"), 
               ('kappaandb', "kap And b"), 
               ('pds70b', "PDS 70 b"), 
               ('pztelb', "PZ Tel b"), 
               ('ross458b', "Ross 458 b"), 
               ('twa5b', "TWA 5 b")]

class ReusableForm(FlaskForm):
    planetname = SelectField('Planet Name:', [DataRequired()], choices=multchoices, default = 0)
    time = DateField("Time:", [DataRequired()], default = date.today())
    submit = SubmitField("Generate Coordinates", [DataRequired()])

def truncate(n, decimals=0):
    multiplier = 10 ** decimals
    return int(n * multiplier) / multiplier

@app.route('/', methods = ['GET', 'POST'])
def gencoord():
    form = ReusableForm(request.form)
    ra_args = ""
    dec_args = ""
    sep_args = ""
    pa_args = ""
    if request.method == 'POST':
        planet_name = request.form['planetname']
        date_mjd = request.form['time']
        ra_args, dec_args, sep_args, pa_args = whereistheplanet.predict_planet(planet_name, date_mjd)
        ra_args1 = truncate(ra_args[0], 3)
        ra_args2 = truncate(ra_args[1], 3)
        dec_args1 = truncate(dec_args[0], 3)
        dec_args2 = truncate(dec_args[1], 3)
        sep_args1 = truncate(sep_args[0], 3)
        sep_args2 = truncate(sep_args[1], 3)
        pa_args1 = truncate(pa_args[0], 3)
        pa_args2 = truncate(pa_args[1], 3)
        ra_args = "RA Offset = " + str(ra_args1) + " +/- " + str(ra_args2) + " mas"
        dec_args = "Dec Offset = " + str(dec_args1) + " +/- " + str(dec_args2) + " mas"
        sep_args = "Separation = " + str(sep_args1) + " +/- " + str(sep_args2) + " mas"
        pa_args = "PA = " + str(pa_args1) + " +/- " + str(pa_args2) + " deg"
    return render_template('base.html', form=form, ra_args=ra_args, dec_args=dec_args, sep_args=sep_args, pa_args=pa_args)
if __name__ == "__main__":
    app.run()
