# Script:   panologquery.py
# Author:   Kevin Tigges
# Date:     06/20/2026  
# Updated:  07/05 - Modified form and updated query logic
# Version:  0.2
#
# Script will make API calls to panorama to 

import os
import subprocess
import pdb
from flask import Flask, render_template, request, flash
from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap
from wtforms import StringField, SubmitField, IntegerField, DateTimeField, DateField
from wtforms.validators import DataRequired, Length, IPAddress, InputRequired, NumberRange, Optional, Regexp
from query import *
from dotenv import load_dotenv
from datetime import date, datetime, timedelta
import time
import xml.etree.ElementTree as ET


class QueryInputForm(FlaskForm):
  
    f_start_date = DateField('Start Date', format='%Y-%m-%d', validators=[InputRequired()],)
    f_end_date = DateField('Start Date', format='%Y-%m-%d', validators=[InputRequired()])
    f_start_time = StringField('Select Start time (HH:MM)', validators=[InputRequired(), Regexp(r'^([01]\d|2[0-3]):([0-5]\d)$', message='Invalid time format. Use HH:MM.')])
    f_end_time = StringField('Select Start time (HH:MM)', validators=[InputRequired(), Regexp(r'^([01]\d|2[0-3]):([0-5]\d)$', message='Invalid time format. Use HH:MM.')])
    f_source_ip_address =  StringField('Source IP Address', [IPAddress(ipv4=True, ipv6=False, message='Must Be IP Address'), Optional()])
    f_dest_ip_address =  StringField('Destination IP Address', [IPAddress(ipv4=True, ipv6=False, message='Must Be IP Address'), Optional()])
    f_port = StringField('Port to search', [Optional()])
    f_submit = SubmitField('Submit')

from flask import (Flask, url_for, render_template, redirect)


app = Flask(__name__, instance_relative_config=False)
app.config['SECRET_KEY'] = os.urandom(24)
Bootstrap(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    qform = QueryInputForm()
    # Get the settings from the config file
    panorama_ip = get_options()
    start_time = (datetime.now() - timedelta(minutes=30)).strftime("%H:%M")
    end_time = (datetime.now()).strftime("%H:%M")
    if request.method == 'POST' and qform.validate():
        
        xml_results = ""
        source_ip_address = qform.f_source_ip_address.data
        dest_ip_address = qform.f_dest_ip_address.data
        start_time = qform.f_start_date.data.strftime("%Y/%m/%d") + ' ' + qform.f_start_time.data
        end_time = qform.f_end_date.data.strftime("%Y/%m/%d") + ' ' + qform.f_end_time.data
        if (qform.f_port.data == ''):
            port = 'all'
        else:
            port = qform.f_port.data
        
        xml_results = main(panorama_ip, source_ip_address, dest_ip_address, start_time, end_time, port)
        root = ET.fromstring(xml_results)
        entries = root.findall('.//entry')
        return render_template('results.html', entries = entries)
    qform.f_start_date.data = datetime.now()
    qform.f_end_date.data = datetime.now()
    qform.f_start_time.data = start_time
    qform.f_end_time.data = end_time
    return render_template('index.html', pano_ip=panorama_ip, form=qform)


@app.route('/restart', methods=['GET', 'POST'])
def restart():
    return redirect(url_for('index'))

@app.route('/restart2', methods=['GET', 'POST'])    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run()


