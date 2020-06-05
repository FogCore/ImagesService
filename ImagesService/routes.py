import jwt
import grpc
import uuid
import datetime
from flask import request
from ImagesService.db import images_collection
from ImagesService import app, images_service_pb2, images_service_pb2_grpc


users_service_stub = images_service_pb2_grpc.UsersAPIStub(grpc.insecure_channel('UsersService:50050'))  # gRPC stub to work with Users Service


# Route to authenticate and authorize users and generate JWT tokens
@app.route('/auth')
def token():
    account = request.values.get('account')
    service = request.values.get('service')
    scopes = request.values.getlist('scope')
    if account:
        response = users_service_stub.Verify(images_service_pb2.User(username=request.authorization.username,
                                                                     password=request.authorization.password))
        if response.status.code == 200:
            access = []
            for scope in scopes:
                scope_dict = scope.split(':')
                if scope_dict[1].startswith(request.authorization.username + '/') or request.authorization.username == 'scheduling_service':
                    access.append({
                        'type': scope_dict[0],
                        'name': scope_dict[1],
                        'actions': scope_dict[2].split(',')
                    })
            access_token = jwt.encode({'iss': 'auth.docker.com',
                                       'sub': request.authorization.username,
                                       'aud': service,
                                       'iat': datetime.datetime.utcnow(),
                                       'nbf': datetime.datetime.utcnow(),
                                       'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=60),
                                       'jwi': str(uuid.uuid4()),
                                       'access': access},
                                      app.config['PRIVATE_KEY'],
                                      algorithm='RS256',
                                      headers={'kid': app.config['KID']}).decode('utf-8')

            return {'token': access_token}, 200

    return '', 401


# Docker Registry Event Receiving Route
@app.route('/event', methods=['POST'])
def event():
    events = request.json['events']
    for event in events:
        if event['action'] == 'push':
            repository = event['target']['repository']
            tag = event['target']['tag']
            name = event['actor']['name']
            updated = int(datetime.datetime.now().timestamp())

            user = images_collection.find_one({'user': name})
            if user:
                scope_exists = False
                for scope in user['scopes']:
                    if scope['name'] == repository:
                        scope_exists = True
                        if tag not in scope['tags']:
                            scope['tags'].append(tag)
                            scope['updated'] = updated
                        break

                if not scope_exists:
                    user['scopes'].append({'type': 'repository',
                                           'name': repository,
                                           'tags': [tag],
                                           'updated': updated,
                                           'actions': ['push', 'pull']})

                images_collection.replace_one({'user': name}, user)

            else:
                images_collection.insert_one({'user': name,
                                              'scopes': [{'type': 'repository',
                                                          'name': repository,
                                                          'tags': [tag],
                                                          'updated': updated,
                                                          'actions': ['push', 'pull']}]})

        else:
            print('Unknown action: ', event['action'])
            exit(0)

    return '', 200
