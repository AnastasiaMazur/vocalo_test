import datetime

import requests
from flask import Flask, request, g, redirect, render_template, flash, jsonify, session
from flask_bcrypt import Bcrypt
from flask_wtf import CSRFProtect

from flask_mongoengine import MongoEngine

from exceptions import InvalidUsage
from models import *
from settings import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI

app = Flask(__name__)
app.config.from_object('settings')
bcrypt = Bcrypt(app)
csrf = CSRFProtect(app)
db = MongoEngine(app)


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route('/')
def index():
    return render_template('login.html')


@app.route('/oauth2_login')
def oauth2_login():
    url = "https://app.hubspot.com/oauth/authorize?client_id={}&scope=contacts&redirect_uri={}/oauth2/tokens".format(
        CLIENT_ID, REDIRECT_URI)
    return redirect(url, code=302)


@app.route('/oauth2/tokens')
def oauth2_tokens():
    code = request.args.get('code')
    url = "https://api.hubapi.com/oauth/v1/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": "{}/oauth2/tokens&code={}".format(REDIRECT_URI, code)
    }

    data = "grant_type={}&client_id={}&client_secret={}&redirect_uri={}".format(data["grant_type"],
                                                                                data["client_id"],
                                                                                data["client_secret"],
                                                                                data["redirect_uri"])
    tokens = requests.post(url, data=data).json()
    if 'access_token' in tokens:
        token = HubspotToken(access_token=tokens['access_token'], refresh_token=tokens['refresh_token'])
        token.save()

        user_data = requests.get('https://api.hubapi.com/oauth/v1/access-tokens/{}'.format(tokens['access_token'])).json()
        print(user_data)
        user = User(email=user_data['user'], hub_domain=user_data['hub_domain'], token=token)
        user.save()

        session['token'] = token['access_token']
        return redirect('/obtain_data')
    else:
        raise InvalidUsage("Can't get access token!", status_code=400)


@app.route('/obtain_data')
def obtain_data():
    return render_template('obtain_data.html')


@app.route('/hubspot_deal_data')
def hubspot_deal_data():
    token = session['token']
    headers = {'authorization': 'Bearer ' + token}
    hubspot_deal_response = requests.get('https://api.hubapi.com/deals/v1/deal/paged?includeAssociations=true&&properties=dealname',
                                         headers=headers).json()

    token = HubspotToken.objects.get(access_token=token)
    for deal in hubspot_deal_response['deals']:
        if not Deal.objects(deal_id=deal['dealId']):
            try:
                obj = Deal(deal_id=deal['dealId'],
                           name=deal['properties']['dealname']['value'],
                           source=deal['properties']['num_associated_contacts']['source'],
                           close_date=datetime.datetime.fromtimestamp(int(deal['properties']['dealname']['timestamp'])/1000),
                           user=User.objects.get(token=token.id)
                           )
                obj.save()
            except Exception as e:
                raise InvalidUsage(str(e), 401)
    flash('Saved to DB!')
    return jsonify(hubspot_deal_response)


if __name__ == '__main__':
    app.run(host='127.0.0.1')
