import grpc
from flask import Flask
from concurrent import futures
from ImagesService.methods import ImagesAPI
from ImagesService import images_service_pb2_grpc

server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
images_service_pb2_grpc.add_ImagesAPIServicer_to_server(ImagesAPI(), server)
server.add_insecure_port('[::]:50050')

app = Flask(__name__)
app.config.from_pyfile('/ImagesService/config.py')

from ImagesService import routes
