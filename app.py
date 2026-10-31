from flask import Flask, render_template, flash, request
from wtforms import Form, SelectField, SubmitField, validators, ValidationError
from wtforms import BooleanField, DateField
from flask_wtf import FlaskForm
from datetime import date
from functools import lru_cache
from importlib.metadata import version
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
    show_orbit = BooleanField("Show full orbit plot", default=False)

def truncate(n, decimals=0):
    multiplier = 10 ** decimals
    return int(n * multiplier) / multiplier


@lru_cache(maxsize=1)
def _get_plotly_javascript():
    """Load the locally installed plotting bundle only when it is requested."""
    from plotly.offline import get_plotlyjs
    return get_plotlyjs()


@app.route('/orbit-plot.js')
def orbit_plot_javascript():
    response = app.response_class(_get_plotly_javascript(), mimetype='application/javascript')
    response.cache_control.public = True
    response.cache_control.max_age = 86400
    response.add_etag()
    return response.make_conditional(request)


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
    orbit_plot = None
    plotly_version = ""
    plot_error = ""
    planet_label = ""
    
    if request.method == 'POST':
        planet_name = whereistheplanet.resolve_name(request.form.get('planetname', ''))
        date_mjd = request.form.get('time', '')
        if planet_name not in whereistheplanet.display_names:
            error_msg = "Invalid Planet"
        else:
            orbit_data = None
            orbit_failure = None
            try:
                if form.show_orbit.data:
                    try:
                        orbit_data = whereistheplanet.predict_orbit(planet_name, date_mjd)
                    except Exception as exc:
                        # A plot failure must not hide an otherwise valid prediction.
                        orbit_failure = exc
                        prediction = whereistheplanet.predict_planet(planet_name, date_mjd)
                    else:
                        prediction = orbit_data['prediction']
                else:
                    prediction = whereistheplanet.predict_planet(planet_name, date_mjd)
                ra_args, dec_args, sep_args, pa_args = prediction
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
                planet_label = whereistheplanet.display_names[planet_name]
                if orbit_failure is not None:
                    app.logger.warning("Orbit calculation failed for %s: %s", planet_name, orbit_failure)
                    plot_error = "The orbit plot could not be generated. The numerical prediction is still available."
                elif orbit_data is not None:
                    try:
                        from whereistheplanet.orbit_plot import build_orbit_plot
                        plotly_version = version('plotly')
                        orbit_plot = build_orbit_plot(orbit_data, planet_label, date_mjd)
                    except Exception:
                        app.logger.exception("Orbit rendering failed for %s", planet_name)
                        plot_error = "The orbit plot could not be generated. The numerical prediction is still available."

    return render_template('base.html', form=form, ra_args=ra_args, dec_args=dec_args,
                           sep_args=sep_args, pa_args=pa_args, ref_str=ref_str,
                           error_msg=error_msg, position_note=position_note,
                           orbit_plot=orbit_plot, plotly_version=plotly_version, plot_error=plot_error,
                           planet_label=planet_label, date_label=request.form.get('time', ''))
if __name__ == "__main__":
    app.run()
