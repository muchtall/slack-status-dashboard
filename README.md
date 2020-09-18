# slack-status-dashboard
Similar to an in-out board, this is a simple HTML dashboard to allow walk-up kiosk viewers to see the status of department members at a glance.

Dependencies:
* Python3
  * slackstatus
  * emoji
  
Usage example:

  export SLACK_API_TOKEN="xoxb-123456789012-1234567890123-abcDEFGhIjkLmnOpqurstUvwxyz" ; export SLACK_USER_IDS=UB1234567,UC8901234,UD5678901,UE2345678,UF9012345 ; python3 slackstatus.py
