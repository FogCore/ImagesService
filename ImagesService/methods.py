from ImagesService.db import images_collection
from ImagesService import images_service_pb2, images_service_pb2_grpc


class ImagesAPI(images_service_pb2_grpc.ImagesAPIServicer):
    # Returns the list of fog application images
    def List(self, request, context):
        repository = images_collection.find({'user': request.username}) if request.username else images_collection.find({})
        images = []
        for document in repository:
            list = []
            for image in document['scopes']:
                list.append(images_service_pb2.Image(name=image['name'],
                                                     updated=image['updated'],
                                                     tags=image['tags']))
            if len(list):
                images.append(images_service_pb2.Images(username=document['user'], list=list))

        if len(images) != 0:
            status = images_service_pb2.Response(code=200)
            return images_service_pb2.ResponseWithImagesList(status=status, images=images)
        else:
            status = images_service_pb2.Response(code=404, message='User not found or has no images yet.')
            return images_service_pb2.ResponseWithImagesList(status=status)

    # Returns information about specified image of fog application
    def Find(self, request, context):
        user_image = request.name.split('/')
        image_tag = user_image[1].split(':')
        if len(user_image) == 2 and len(image_tag) in [1, 2]:
            required_image = images_collection.find_one({'user': user_image[0]}, {'scopes': {'$elemMatch': {'name': user_image[0] + '/' + image_tag[0]}}})

            if required_image and required_image.get('scopes'):
                scope = required_image['scopes'][0]

                # Check for the required tag
                tag = 'latest' if len(image_tag) == 1 else image_tag[1]
                if tag not in scope['tags']:
                    status = images_service_pb2.Response(code=404, message=f'The specified image does not have tag "{tag}".')
                    return images_service_pb2.ResponseWithImage(status=status)

                status = images_service_pb2.Response(code=200, message='Image with the specified name was found.')
                image = images_service_pb2.Image(type=scope['type'],
                                                 name=scope['name'],
                                                 updated=scope['updated'],
                                                 tags=scope['tags'],
                                                 actions=scope['actions'])
                return images_service_pb2.ResponseWithImage(status=status, image=image)
            else:
                status = images_service_pb2.Response(code=404, message='Image with this name not found.')
                return images_service_pb2.ResponseWithImage(status=status)

        status = images_service_pb2.Response(code=422, message='Image name parameter is required. It should consist of a username and an image name, such as <username>/<imagename>:<tag>. Tag parameter is optional.')
        return images_service_pb2.ResponseWithImage(status=status)

    # Removes the image of fog application
    def Delete(self, request, context):
        image_name = request.name.split('/')
        if len(image_name) == 2:
            mongo_result = images_collection.update_one({'user': image_name[0]},
                                                        {'$pull': {'scopes': {'name': request.name}}})

            if not mongo_result.modified_count:
                return images_service_pb2.Response(code=404, message='Image with the specified name was not found.')

            return images_service_pb2.Response(code=200, message='Image with the specified name has been deleted.')

        return images_service_pb2.Response(code=422, message='Image name parameter is required. It should consist of a username and an application name, such as username/imagename.')
