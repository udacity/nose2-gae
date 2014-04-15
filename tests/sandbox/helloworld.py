from google.appengine.ext import webapp

class ImportStuff(webapp.RequestHandler):
    def get(self):
        # this should fail because of the import restrictions
        import webtest
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('Hello world!')

class WriteStuff(webapp.RequestHandler):
    def get(self):
        # this should fail because we can't write files on GAE
        with open('temp.py', 'a') as f:
            f.write('# deleteme')
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('Hello world!')

app = webapp.WSGIApplication([
    ('/import', ImportStuff),
    ('/write', WriteStuff),
], debug=True)
