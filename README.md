Interfaces to queue song paths for Moonbase59's implementation of ices0

# First time setup

cd into `dev_ops` and run script `./mcr_dev_ops.sh setup_tests`


## Database setup/update
`./mcr_dev_ops.sh setup_tests` will also ensure that the database has latest 
available schema changes

## Self-signed certificates
`./mcr_dev_ops.sh setup_tests` will also ensure that a current certificate exists.

# Ways to run api

You can run the server through
nginx
```

#from inside dev_ops
# ./mcr_dev_dev.ah deploy_local_app
```

## To debug through ngnix 
Run `./mcr_dev_ops.sh deploy_local_app`

In vs code, use the launch profile Python: nginx API


## VSCode debug
Use debug launch profile "Python: API"

### For client code

#### First time
`npm i`

#### Starting front end

`npm start`

# Deploying to server

## Fresh Server
```
`./mcr_dev_ops.sh setup_new_box`

```
