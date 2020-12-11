import os
import cgi
import re
import html
import sys

from pysummarization.nlpbase.auto_abstractor import AutoAbstractor
from pysummarization.tokenizabledoc.simple_tokenizer import SimpleTokenizer
from pysummarization.abstractabledoc.top_n_rank_abstractor import TopNRankAbstractor
from summarize import summarize
from http.server import BaseHTTPRequestHandler, HTTPServer

class Summarize(BaseHTTPRequestHandler):
  def output(self, template, context):
    def replace(match):
      return html.escape(str(context[match.group(1)]))

    self.send_response(200)
    self.send_header('Content-type', 'text/html')
    self.send_header('Connection', 'close')
    self.end_headers()
    self.wfile.write(re.sub('\{\{([^}]+)\}\}', replace, self.templates[template]).encode())

  def do_GET(self):
    self.output('form', {})

  def do_POST(self):
    form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD': 'POST'})
    text = form.getvalue('text')
    sentences = int(form.getvalue('sentences'))

    if text is None:
      self.output('result', {'text': '', 'result': '', 'sentences': sentences})
    else:
      graph_result = summarize(text, sentence_count=sentences, language=form.getvalue('language'))

      auto_abstractor = AutoAbstractor()
      auto_abstractor.tokenizable_doc = SimpleTokenizer()
      auto_abstractor.delimiter_list = ['.', "\n"]
      rank = TopNRankAbstractor()
      rank.top_n = sentences
      result_dict = auto_abstractor.summarize(text, rank)

      self.output('result', {
        'text'        : text,
        'result.graph': graph_result,
        'result.ai'   : ''.join(result_dict['summarize_result']),
        'sentences'   : sentences
      })

if __name__ == '__main__':
  handler = Summarize
  handler.templates = {}

  path = os.path.dirname(sys.argv[0])
  for file in os.listdir(path):
    if file.endswith('.html'):
      with open(os.path.join(path, file), 'r', encoding='utf8') as f:
        handler.templates[os.path.basename(file)[0 : -5]] = f.read()

  try:
      port = 8080
      server = HTTPServer(('', port), handler)
      print("Web Server running on port %s" % port)
      server.serve_forever()
  except KeyboardInterrupt:
      print("stopping web server....")
      server.socket.close()