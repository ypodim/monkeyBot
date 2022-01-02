
import tornado.ioloop
import tornado.iostream
import tornado.web
import tornado.template
import tornado.locks
import video
import os
from collections.abc import MutableMapping
from tornado.options import define, options

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
    def initialize(self, store):
        self.store = store
    def get(self):
        self.render('index.html')

class StreamHandler(tornado.web.RequestHandler):
    def initialize(self, cam):
        self.cam = cam
    async def get_frame(self):
        # self.jpg, image = self.cam.get_frame(True)

        jpg = None
        grabbed_frame = False
        try:
            jpg = self.cam.q.get(block=False)
            grabbed_frame = True
            self.cam.q.task_done()
        except:
            pass
            # if last_image is None:
                # continue
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
            self.write('Content-length: %s\r\n\r\n' % len(self.jpg))
            self.write(jpg) # self.jpg must die
            self.write(b'\r\n')
            try:
                await self.flush()
            except tornado.iostream.StreamClosedError:
                print("stupid client left. Good riddance.")
                return

class Application(tornado.web.Application):
    def __init__(self, store, cam):
        handlers = [
            (r"/", HtmlPageHandler, dict(store=store)),
            (r"/video_feed", StreamHandler, dict(cam=cam)),
            (r'/favicon.ico', tornado.web.StaticFileHandler),
            (r'/static/', tornado.web.StaticFileHandler),
            (r'/(?:js)/(.*)', tornado.web.StaticFileHandler, dict(path='./js')),
        ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "www"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            debug=True,
        )
        super(Application, self).__init__(handlers, **settings)


async def main(shutdown_event):
    tornado.options.parse_command_line()
    # tornado.log.enable_pretty_logging()

    cam = video.UsbCamera()
    store = Store()
    app = Application(store, cam)
    
    io_loop = tornado.ioloop.IOLoop.current()
    app.listen(options.port)
    await shutdown_event.wait()


if __name__ == "__main__":
    shutdown_event = tornado.locks.Event()
    try:
        tornado.ioloop.IOLoop.current().run_sync(lambda: main(shutdown_event))
    except KeyboardInterrupt:
        print("time to die")
        shutdown_event.set()


