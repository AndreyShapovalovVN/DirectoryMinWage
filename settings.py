import os

DEBUG = True

APP_PORT = os.environ.get('LISTEN_PORT') or 8060

# token sha512 от userid
USERID = os.environ.get('userId') or '0123456789'
TOKEN = 'bb96c2fc40d2d54617d6f276febe571f623a8dadf0b734855299b0e107fda32cf6b69f2da32b36445d73690b93cbd0f7bfc20e0f7f28553d2a4428f23b716e90'
