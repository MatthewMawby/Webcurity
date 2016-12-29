# Webcurity

Webcurity utilizes Opencv to allow users to use a webcam as a security camera. Webcurity detects motion, snaps pictures, and emails you so you can keep an eye at home when you're not there.

Using webcurity is simple:
  1. Clone the repository
  2. Configure settings.json
    * email : the email notifications will be sent to
    * min_contour : the minimum area in pixels that must change from one frame to the next to register as "motion"
    * email_notifications : boolean value to turn email notifcations on/off
    * xres & yres : the resolution to be captured
    * record_time : the time in seconds of clips to be captured after motion has been detected
  3. [Turn on the gmail api](https://developers.google.com/gmail/api/quickstart/python#step_1_turn_on_the_api_name) & save "client_secret.json" to the top level "Webcurity" directory
  4. Set up your webcam in a stable location pointed away from light (causes focusing issues)
  5. Start the python script!

Compatibility patches will be coming soon to ensure webcurity can run properly on Raspian so this can be run on a raspberry pi.

If you have any questions, comments, or contributions please create an issue or submit a pr.
Thanks!
