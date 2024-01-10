import logging
import json
import os
import asyncio
import tornado
from tornado import httputil

def normalize_header(name: str) -> str:
    if name.startswith("icy-") or name.startswith("ice-audio-info"):
        return name
    return "-".join([w.capitalize() for w in name.split("-")])

httputil._normalize_header = normalize_header

# use pycurl for AsyncHTTPClient
tornado.httpclient.AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")

def load_streams(filename):
    if os.path.exists(filename):
        with open(filename) as f:
            streams = json.loads(f.read())
    else:
        streams = {}
    return streams

class RadioStreamHandler(tornado.web.RequestHandler):

    def initialize(self, streams={}):
        self.streams = streams

    @tornado.gen.coroutine
    def get(self, stream_name, stream_fmt):
        while True:
            try:
                logger = logging.getLogger("RadioStreamHandler")
                logger.debug("Connection from {}".format(self.request.remote_ip))
                logger.debug("Requested stream: {}".format(stream_name))

                # get the stream url from config file
                if stream_name not in self.streams:
                    logger.error("Stream not found: {}".format(stream_name))
                    self.set_status(404)
                    self.finish()
                    return
                stream_array = self.streams[stream_name]
                stream_url = stream_array[0]
                stream_fmt = stream_array[1]

                # build headers to send to server
                icy_headers = {}
                for header in self.request.headers:
                    if header.lower().startswith("icy"):
                        icy_headers[header] = self.request.headers[header]
                        logger.debug("Additional header: '{0}: {1}'".format(header, icy_headers[header]))

                # prepare client
                client = tornado.httpclient.AsyncHTTPClient()

                # resolve redirects
                request = tornado.httpclient.HTTPRequest(stream_url, method="HEAD",
                                                        headers=icy_headers,
                                                        request_timeout=0)
                try:
                    response = yield client.fetch(request)
                except tornado.httpclient.HTTPError as e:
                    pass
                except Exception as e:
                    self.finish()
                    break
                else:
                    if response.effective_url != stream_url:
                        logger.debug("Redirected. New URL: {}".format(response.effective_url))
                    stream_url = response.effective_url

                # connect to stream and proxy data to client
                logger.debug("Starting stream...")
                request = tornado.httpclient.HTTPRequest(stream_url,
                                                        headers={"icy-metadata": "1"},
                                                        streaming_callback=self.stream_callback,
                                                        header_callback=self.header_callback,
                                                        request_timeout=0)
                yield client.fetch(request, self.async_callback)
            except tornado.httpclient.HTTPError as e:
                print("HTTPError: "+str(e))
                break
            except Exception as e:
                print(e)
                break

    async def async_callback(self, response):
        try:
            await self.flush()
        except tornado.iostream.StreamClosedError:
            return

    def stream_callback(self, chunk):
        self.write(chunk)
        self.flush()

    def header_callback(self, header_line):
        d = header_line.strip().split(":", 1)
        if len(d) != 2:
            return
        if d[0].lower().startswith("icy-"):
            self.set_header(d[0], d[1].strip())
        if d[0].lower().startswith("ice-audio-info"):
            self.set_header(d[0], d[1].strip())
        if d[0].lower().startswith("content-type"):
            if d[1].strip() == "audio/aacp":
                self.set_header(d[0], "audio/aac")
            else:
                self.set_header(d[0], d[1].strip())
        if d[0].lower().startswith("connection"):
            self.set_header(d[0], d[1].strip())

def run_server(filename, port=8080, address='localhost'):
    application = tornado.web.Application([
        (r"/radio/([^.]+)\.([^.]+)", RadioStreamHandler,
         dict(streams=load_streams(filename)))
        ])
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(port, address)
    tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger("RadioStreamHandler").setLevel(logging.DEBUG)
    run_server("../../streams.json")
