from flask import Flask, render_template, flash, request
from wtforms import Form, SelectField, SubmitField, validators, ValidationError
from wtforms import DateField
from flask_wtf import FlaskForm
from datetime import date
from wtforms.validators import DataRequired
import configparser
import sys
sys.path.append("./whereistheplanet/") #Example
import whereistheplanet

### Read secret key from flask.ini file
### YOU MUST MAKE YOUR OWN THAT IS A COPY OF flask.ini.default
config = configparser.ConfigParser()
config.read("flask.ini")
token = config.get('DEFAULT', 'token')


app = Flask(__name__)
app.secret_key = token

multchoices = [("", 'Choose one'),
               ("hr8799b", "HR 8799 b"), 
               ("hr8799c", "HR 8799 c"), 
               ("hr8799d", "HR 8799 d"), 
               ('hr8799e', "HR 8799 e"), 
               ('betapicb', "bet Pic b"), 
               ('betapicc', "bet Pic c"),
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
               ('pds70c', "PDS 70 c"), 
               ('pztelb', "PZ Tel b"), 
               ('ross458b', "Ross 458 b"), 
               ('twa5b', "TWA 5 b"),
               ('hip64892b', "HIP 64892 b"),
               ('2m0103b', "2M0103b"),
               ('roxs42b', "ROXs 42 Bb"),
               ('roxs12b', "ROXs 12 b"),
               ('gqlupb', "GQ Lup b"),
               ('gsc6214-210b', "GSC 6214-210 b"),
               ('hip79098ABb', "HIP 79098 ABb"),
               ('gsc08047-00232b', "GSC 08047-0023 b"),
               ('2m0122b', "2M0122b"),
               ('gj758b', "GJ 758 b"),
               ('hd4747b', "HD 4747 b"),
               ('fwtauc', "FW Tau C"),
               ('hd284149abb', "HD 284149 ABb"),
               ('hd72946b', "HD 72946 b"),
               ('hd13724b', "HD 13724 b"),
               ('gl229b', "Gl 229 b"),
               ('hd33632b', "HD 33632 b")]

multchoices.sort()

class ReusableForm(FlaskForm):
    planetname = SelectField('Planet Name: ', [DataRequired()], choices=multchoices, default = 0)
    time = DateField("Date: ", default = date.today, format='%Y-%m-%d')

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
    error_msg = ""
    ref_str = ""
    
    if request.method == 'POST':
        planet_name = request.form['planetname']
        date_mjd = request.form['time']

        try:
            ra_args, dec_args, sep_args, pa_args = whereistheplanet.predict_planet(planet_name, date_mjd)
            ref = whereistheplanet.get_reference(planet_name)
        except ValueError:
            error_msg = "Invalid Date"
        except KeyError:
            error_msg = "Invalid Planet"

        ra_args = "RA Offset = {0:.3f} +/- {1:.3f} mas".format(ra_args[0], ra_args[1])
        dec_args = "Dec Offset = {0:.3f} +/- {1:.3f} mas".format(dec_args[0], dec_args[1])
        sep_args = "Separation = {0:.3f} +/- {1:.3f} mas".format(sep_args[0], sep_args[1])
        pa_args = "PA = {0:.3f} +/- {1:.3f} deg".format(pa_args[0], pa_args[1])
        ref_str = "Reference: {0}".format(ref)

    return render_template('base.html', form=form, ra_args=ra_args, dec_args=dec_args, sep_args=sep_args, pa_args=pa_args, ref_str=ref_str, error_msg=error_msg)
if __name__ == "__main__":
    app.run()
