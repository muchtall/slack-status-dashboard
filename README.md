# slack-status-dashboard
*Does your department have walk-up visitors that have a common question? **"Is so-and-so in today?"***

Similar to an in-out board, this is a simple HTML dashboard to allow walk-up kiosk viewers to see the status of department members at a glance.

Screenshot:

![Screenshot](https://user-images.githubusercontent.com/16903291/93802694-68b7c280-fc09-11ea-8ef8-8f7ebcb3ac22.png "Dashboard")

To build:

    docker build -t muchtall/slack-status-dashboard  

Usage example:

     docker run -d --env SLACK_API_TOKEN="xoxb-123456789012-1234567890123-abcDEFGhIjkLmnOpqurstUvwxyz" --env SLACK_USER_IDS=UB1234567,UC8901234,UD5678901,UE2345678,UF9012345 --env PAGE_HEADER="IT Department Status" --name slack-status-dashboard -p 8880:8880  muchtall/slack-status-dashboard

The script polls the Slack API every ~60 seconds. The page refreshes itself in the browser every 5 seconds.

This is intended to work in concert with https://github.com/muchtall/slack-status-updater

Google fodder: Slack Status In-Out Board
