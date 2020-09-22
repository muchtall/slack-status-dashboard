#!/usr/bin/python3
import time
import sys
import os
import urllib
import json
#import emoji
import logging
from slack import WebClient
from slack.errors import SlackApiError
from flask import Flask, request, send_from_directory
from waitress import serve
import os
import re
from multiprocessing import Process

logging.getLogger('waitress')
logging.basicConfig(level=logging.INFO)
logging.setLevel(logging.INFO)

output_filename = "slack-status-dashboard.html"
slack_token = os.environ["SLACK_API_TOKEN"]
slack_user_ids = os.environ["SLACK_USER_IDS"].split(',')
page_header = os.environ["PAGE_HEADER"]

### Waitress server
if not os.path.exists('static'):
    os.makedirs('static')
output_static_path = 'static/' + output_filename

app = Flask(__name__, static_url_path='')

@app.route('/')
def root():
    return app.send_static_file(output_filename)

def webserver():
    logging.info("Webserver process started.")
    serve(app, listen='*:8880')

def dashboard():
  ### Slack dashboard
  logging.info("Dashboard process started.")

    # Get a dictionary of emojis (since emoji/emojize doesn't cover them all)
  with urllib.request.urlopen('https://raw.githubusercontent.com/iamcal/emoji-data/master/emoji.json') as standard_emoji_response:
    emoji_dict = json.loads(standard_emoji_response.read().decode())

  client = WebClient(token=slack_token)
  
  def GetUserInfo(users_list, user_id):
    return [obj for obj in users_list if obj['id']==user_id]
  
  
  try:
    emoji_response = client.emoji_list()
  except SlackApiError as e:
    logging.error(e)
    logging.error("Unexpected error:", sys.exc_info()[0])
    #raise
  custom_emoji_list = emoji_response.data['emoji']
  
  while True:
    #print("\033c")
    html_output = ['<html><head><title>' + page_header + '</title>']
    html_output.append('<style>')
    html_output.append('@font-face{font-family:Slack-Lato;font-style:normal;font-weight:400;src:local("\263A"),url(https://a.slack-edge.com/bv1-8-83658ee/lato-regular-d9ce515.woff2) format("woff2"),url(https://a.slack-edge.com/bv1-8-83658ee/lato-regular-ea6d1e4.woff) format("woff");unicode-range:U+0000-f8fe,U+f900-ffff}')
    html_output.append('@font-face{font-family:Slack-Lato;src:url(https://a.slack-edge.com/bv1-8-83658ee/slack-icons-v2-bd8eec0.woff2) format("woff2"),url(https://a.slack-edge.com/bv1-8-83658ee/slack-icons-v2-36256a5.woff) format("woff");font-style:normal;font-weight:400; unicode-range:U+e506-e508,U+e535-e535;}')
    html_output.append('body {font-family: Slack-Lato;}')
    html_output.append('table.center {margin-left:auto; margin-right:auto;}')
    html_output.append('</style>')
    html_output.append('<link rel="stylesheet" href="https://a.slack-edge.com/bv1-8-83658ee/client-boot-styles.fc78710.css?cacheKey=gantry-1594776859">')
    html_output.append('<meta http-equiv="refresh" content="5">')
    html_output.append('</head><body><table class="center" style="text-align: left; font-family: \'Slack-Lato\'">')
    html_output.append("<thead ><tr><th colspan=\"4\" style=\"text-align: center;\">" + page_header + "<br><br></tr></thead>")
    html_output.append("<tbody>")
  
    ### Get the list of users and their attributes
    try:
      response = client.users_list()
    except SlackApiError as e:
      if e.response["error"] == "ratelimited":
        delay = int(e.response.headers['Retry-After'])
        logging.warning(f"Rate limited. Retrying in {delay} seconds")
        time.sleep(delay)
        response = client.users_list()
    except:
      logging.warning("Unexpected error:", sys.exc_info()[0])
      #raise

    try:
      users_list = response.data['members']
    except:
      logging.error("Unexpected error:", sys.exc_info()[0])

    ### Get the dnd state of the users we care about
    try:
      response = client.dnd_teamInfo(users=slack_user_ids)
    except SlackApiError as e:
      if e.response["error"] == "ratelimited":
        delay = int(e.response.headers['Retry-After'])
        logging.warning(f"Rate limited. Retrying in {delay} seconds")
        time.sleep(delay)
        response = client.dnd_teamInfo(users=slack_user_ids)
    except:
      logging.error("Unexpected error:", sys.exc_info()[0])
      #raise
    dnd_users = response.data['users']
  
    for user_id in slack_user_ids:
      
      userdata = GetUserInfo(users_list,user_id)[0]
      userprofile = userdata['profile']
      status = userprofile['status_text']
      status_emoji = userprofile['status_emoji'].replace(':','')
      real_name = userdata['real_name']
  
  
      try:
        response = client.users_getPresence(user=user_id)
      except SlackApiError as e:
          if e.response["error"] == "ratelimited":
            delay = int(e.response.headers['Retry-After'])
            logging.warning(f"Rate limited. Retrying in {delay} seconds")
            time.sleep(delay)
            response = client.client.users_getPresence(user=user_id)
      except:
        logging.error("Unexpected error:", sys.exc_info()[0])
        #raise
  
      presence = response.data['presence']
  
      dnd_enabled = dnd_users[user_id]['dnd_enabled']
      if dnd_enabled == 1:
        if dnd_users[user_id]['next_dnd_start_ts'] < time.time() < dnd_users[user_id]['next_dnd_end_ts']:
          dnd_state = '/dnd'
        else:
          dnd_state = ''
      else:
        dnd_state = ''
  
      if status_emoji:
        try:
          status_emoji_url = custom_emoji_list[status_emoji]
        except:
          #emoji_code = emoji.emojize(':'+status_emoji+':').lower()
          #emoji_code_lower = f'{ord(emoji_code):X}'.lower()
          for emoji_entry in emoji_dict:
            if emoji_entry["short_name"].lower() == status_emoji.lower():
              emoji_code_lower = emoji_entry["unified"].lower()
              break
          status_emoji_url = 'https://a.slack-edge.com/production-standard-emoji-assets/10.2/google-large/' + emoji_code_lower + '.png'
      else:
        status_emoji_url = ''
  
      if sys.stdout.isatty():
        print('{:<30}{:<20}{:<30}{:<20}{:<100}'.format(real_name,presence+dnd_state,status,status_emoji,status_emoji_url))
      if status_emoji_url:
        status_emoji_html = "<img src=\""+status_emoji_url+"\" width=\"12\" height=\"12\">"
      else:
        status_emoji_html = ''
      
      if presence == "active" and dnd_state == "":
        presence_icon = "<p style=\"color:green;\">\ue506</p>"   
      elif presence == "away" and dnd_state == "":
        presence_icon = "<p style=\"color:grey;\">\ue507</p>"
      elif presence == "active" and dnd_state == "/dnd":
        presence_icon = "<p style=\"color:green;\">\ue508</p>"
      elif presence == "away" and dnd_state == "/dnd":
        presence_icon = "<p style=\"color:grey;\">\ue535</p>"
      else:
        presence_icon = ""
  
      html_line = "<tr><th>"+presence_icon+"</th><th>"+real_name+"</th><th>"+status_emoji_html+" "+status+"</th></tr>"
      html_output.append(html_line)
    html_output.append("</tbody>")
    html_output.append("</table></p></body></html>")
    with open(output_static_path, mode='wt', encoding='utf-8') as myfile:
      myfile.write('\n'.join(html_output))

    if sys.stdout.isatty():
      print()

    logging.info("Refresh run completed.")

    time.sleep(60)

if __name__ == "__main__":
    webserver = Process(target = webserver)
    dashboard = Process(target = dashboard)
    webserver.start()
    dashboard.start()
