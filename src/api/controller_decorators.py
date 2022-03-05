
import time
import cherrypy



def check_access(func):
  def wrap(*args, **kwargs):
    print(cherrypy.request.header_list)
    if "lastVisited" in cherrypy.session:
      print(cherrypy.session["lastVisited"])
    cherrypy.session["lastVisited"] = time.time()
    result = func(*args, **kwargs)
    return result
  return wrap