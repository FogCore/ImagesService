# Images Service

This service provides access to applications images repository. To work with the FogCore platform each user uploads an image of his software to the repository. This image will be executed in containers on fog devices.

The service consists of 3 components:

1. **ImagesService** – Python script
2. **MongoDB** – Database
3. **DockerRegistry** – Docker Images Repository



The service provides gRPC API methods.

**All gRPC methods can return:**

1. **code**=500, **message**="An internal server error has occurred."



## List

Returns the list of fog application images.

#### Parameters:

Receives a message of User type.

1. **username**. Unique user login in the system. If this parameter is skipped, all images in the system are returned.

#### Result:

Returns a message of ResponseWithImagesList type.

1. **status**=(**code**=200), **images**=[ ( **username**=string, **list**=[ (**name**=string, **updated**=int64, **tags**=[ string ] ) ] ) ]
2. **status**=(**code**=404, **message**="User not found or has no images yet.")



## Find

Returns information about specified image of fog application.

#### Parameters:

Receives a message of Image type.

1. **name**. Image name in format &lt;username&gt;/&lt;imagename&gt;:&lt;tag&gt;. Tag parameter is optional.

#### Result:

Returns a message of ResponseWithImage type.

1. **status**=(**code**=200, **message**="Image with the specified name was found."), **image**=(**type**=string, **name**=string, **updated**=int64, **tags**=[ string ], **actions**=[ string ])
2. **status**=(**code**=404, **message**="The specified image does not have tag &lt;tag&gt;.")
3. **status**=(**code**=404, **message**="Image with this name not found.")
4. **status**=(**code**=422, **message**="Image name parameter is required. It should consist of a username and an image name, such as &lt;username&gt;/&lt;imagename&gt;:&lt;tag&gt;. Tag parameter is optional.")



## Delete

Removes the image of fog application.

#### Parameters:

Receives a message of Image type.

1. **name**. Image name in format &lt;username&gt;/&lt;imagename&gt;.

#### Result:

Returns a message of Response type.

1. **status**=(**code**=200, **message**="Image with the specified name has been deleted.")
2. **status**=(**code**=404, **message**="Image with the specified name was not found.")
3. **status**=(**code**=422, **message**="Image name parameter is required. It should consist of a username and an application name, such as username/imagename.")



# REST methods

REST methods are only used by Docker Registry.

## `GET` /auth

Route to authenticate and authorize users and generate JWT tokens.

## `POST` /event

Docker Registry Event Receiving Route.


**The reported project was supported by RFBR, research project No. 18-07-01224**
