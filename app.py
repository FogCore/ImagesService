#!/usr/bin/env python3

from ImagesService import app, server

if __name__ == '__main__':
    server.start()
    app.run(host='0.0.0.0', port=80)
