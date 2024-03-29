#!/usr/bin/env python3

import tornado.ioloop
import tornado.iostream
import tornado.web
import tornado.template
# import tornado.locks
import video
import asyncio
import os
import signal
import logging
import functools
import time
from collections.abc import MutableMapping
from tornado.options import define, options

from bot import Bot

define("port", default=8000, help="run on the given port", type=int)
# define("html_path", default=os.path.dirname(os.path.realpath(__file__)) + '/www/', type=str)
# html_page_path = dir_path = os.path.dirname(os.path.realpath(__file__)) + '/www/'

class Store(MutableMapping):
    def __init__(self, *args, **kwargs):
        self.store = dict(data=None)
        self.last_update = 0
        self.actions = []
        self.update(dict(*args, **kwargs))  # use the free update to set keys
    def __getitem__(self, key):
        return self.store[self.__keytransform__(key)]

    def __setitem__(self, key, value):
        self.last_update = datetime.datetime.now()
        self.store[self.__keytransform__(key)] = value

    def __delitem__(self, key):
        del self.store[self.__keytransform__(key)]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def __repr__(self):
        return "%s" % self.store

class HtmlPageHandler(tornado.web.RequestHandler):
    # def initialize(self, store):
        # self.store = store
    def get(self):
        self.render('index.html')

class CommandHandler(tornado.web.RequestHandler):
    def initialize(self, bot):
        self.bot = bot
    async def post(self):
        cmd = self.get_argument('cmd')
        self.bot.run(cmd)
        self.write(dict(result="ok", cmd=cmd))

class StreamHandler(tornado.web.RequestHandler):
    def initialize(self, cam):
        self.cam = cam
    async def get_frame(self):
        jpg = None
        grabbed_frame = False
        try:
            # print(self.cam.q.qsize())
            jpg = self.cam.q.get(block=False)
            grabbed_frame = True
            self.cam.q.task_done()
        except:
            pass
        return grabbed_frame, jpg

    async def get(self):
        self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, pre-check=0, post-check=0, max-age=0')
        self.set_header('Pragma', 'no-cache')
        self.set_header('Content-Type', 'multipart/x-mixed-replace;boundary=FRAME')
        self.set_header('Connection', 'close')

        my_boundary = "--FRAME\r\n"

        while 1:
            grabbed_frame, jpg = await self.get_frame()
            if not grabbed_frame:
                await asyncio.sleep(0.01)
                continue

            self.write(my_boundary)
            self.write('Content-Type: image/jpeg\r\n')
            self.write('Content-length: %s\r\n\r\n' % len(jpg))
            self.write(jpg) # self.jpg must die
            self.write(b'\r\n')
            # print("wrote data to stream: %s" % (time.time() - start))
            try:
                await self.flush()
                await asyncio.sleep(0.0001)
            except tornado.iostream.StreamClosedError:
                print("stupid client left. Good riddance.")
                return
            # print("end of loop: %s" % (time.time()-start))

class Application(tornado.web.Application):
    def __init__(self):
        io_loop = tornado.ioloop.IOLoop.current()
        self.cam = video.UsbCamera().start()
        self.bot = Bot(io_loop)
        handlers = [
            (r"/", HtmlPageHandler),
            (r"/index.html", HtmlPageHandler),
            (r"/command", CommandHandler, dict(bot=self.bot)),
            (r"/video_feed", StreamHandler, dict(cam=self.cam)),
            (r'/favicon.ico', tornado.web.StaticFileHandler),
            (r'/static/', tornado.web.StaticFileHandler),
            (r'/(?:js)/(.*)', tornado.web.StaticFileHandler, dict(path='./js')),
            (r'/(favicon.ico)', tornado.web.StaticFileHandler, dict(path='./static')),
        ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "www"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            debug=True,
        )
        super(Application, self).__init__(handlers, **settings)

    def start(self):
        tornado.options.parse_command_line()
        tornado.log.enable_pretty_logging()
                
        signal.signal(signal.SIGTERM, functools.partial(self.sig_handler))
        signal.signal(signal.SIGINT, functools.partial(self.sig_handler))

        self.listen(options.port)
        tornado.ioloop.IOLoop.instance().start()

    def sig_handler(self, sig, frame):
        logging.warning('Caught signal: %s', sig)
        tornado.ioloop.IOLoop.instance().stop()
        self.bot.cleanup()
        self.cam.stop()

if __name__ == "__main__":
    app = Application()
    app.start()

