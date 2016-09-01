# Description:
#  This is the DB connection configuration file. To get scripts working, the
#  below class DbConfig should be properly filled.

class DbConfig:
  username = None
  password = None
  host = None
  db = None

  def __init__(self):
    return

  def __str__(self):
    buf = "DbConfig [host=%s / db=%s / username=%s / password=<***>]" % (str(self.host), str(self.db), str(self.username))
    return buf

  def __repr__(self):
    buf = "<DbConfig>"
    return buf
