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

# Public labels and files come from the same catalog used by the library.
multchoices = [("", "Choose one")] + sorted(whereistheplanet.display_names.items())

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
    position_note = ""
    
    if request.method == 'POST':
        planet_name = whereistheplanet.resolve_name(request.form.get('planetname', ''))
        date_mjd = request.form.get('time', '')
        if planet_name not in whereistheplanet.display_names:
            error_msg = "Invalid Planet"
        else:
            try:
                ra_args, dec_args, sep_args, pa_args = whereistheplanet.predict_planet(planet_name, date_mjd)
                ref = whereistheplanet.get_reference(planet_name)
            except (ValueError, TypeError):
                ra_args = dec_args = sep_args = pa_args = ""
                error_msg = "Invalid Date"
            else:
                ra_args = "RA Offset = {0:.3f} +/- {1:.3f} mas".format(*ra_args)
                dec_args = "Dec Offset = {0:.3f} +/- {1:.3f} mas".format(*dec_args)
                sep_args = "Separation = {0:.3f} +/- {1:.3f} mas".format(*sep_args)
                pa_args = "PA = {0:.3f} +/- {1:.3f} deg".format(*pa_args)
                ref_str = "Reference: {0}".format(ref)
                position_note = whereistheplanet.get_position_note(planet_name)

    return render_template('base.html', form=form, ra_args=ra_args, dec_args=dec_args, sep_args=sep_args, pa_args=pa_args, ref_str=ref_str, error_msg=error_msg, position_note=position_note)
if __name__ == "__main__":
    app.run()
