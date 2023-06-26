# Script:   panologquery.py
# Author:   Kevin Tigges
# Date:     06/20/2026  
# Version:  0.1
#
# Script will make API calls to panorama to 

import os
import subprocess
import pdb
from flask import Flask, render_template, request, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, DateTimeField
from wtforms.validators import DataRequired, Length, IPAddress, InputRequired, NumberRange, Optional
from query import *
from dotenv import load_dotenv
import xml.etree.ElementTree as ET


class QueryInputForm(FlaskForm):
    start_time = datetime.now() - timedelta(minutes = 5)
    end_time = datetime.now()
    f_ip_address = StringField('IP Address to search', [InputRequired(), IPAddress(ipv4=True, ipv6=False, message='Must Be IP Address')])
    # f_start_date = DateTimeField('Starting Time Range', format='%Y/%m/%d %H:%M:%S', default=start_time)
    f_end_date =  DateTimeField('Starting Date/Time', format='%Y/%m/%d %H:%M:%S', default=end_time)
    f_minutes = IntegerField('Number of minutes back to search', [InputRequired(), NumberRange(min=1)], default=5)
    f_port = StringField('Port to search', [Optional()])
    f_submit = SubmitField('Submit')

from flask import (Flask, url_for, render_template, redirect)


app = Flask(__name__, instance_relative_config=False)
app.config['SECRET_KEY'] = os.urandom(24)

@app.route('/', methods=['GET', 'POST'])
def index():
    qform = QueryInputForm()
    # Get the settings from the config file
    panorama_ip = get_options()
    if request.method == 'POST' and qform.validate():
        
        xml_results = ""
        ip_address = qform.f_ip_address.data
        minutes = qform.f_minutes.data
        end_time = qform.f_end_date.data
        if (qform.f_port.data == ''):
            port = 'all'
        else:
            port = qform.f_port.data
        
        xml_results = main(panorama_ip, end_time, minutes, ip_address, port)
        root = ET.fromstring(xml_results)
        entries = root.findall('.//entry')
        return render_template('results.html', entries = entries)
    return render_template('index.html', pano_ip=panorama_ip, form=qform)


@app.route('/restart', methods=['GET', 'POST'])
def restart():
    return redirect(url_for('index'))
    

if __name__ == '__main__':
    app.run()


