mongo <<EOF
    use images_service
    db.images.createIndex({user: 1}, {unique: true})
    db.createUser({user: 'images_service', pwd: 'images_service_pwd', roles: [ 'readWrite' ]})
EOF
