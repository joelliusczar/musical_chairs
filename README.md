Interfaces to queue song paths for Moonbase59's implementation of ices0

# First time setup

cd into `dev_ops` and run script `./mcr_dev_ops.sh setup_tests`


# Set up API for testing


Need to run this so that https will work

```
To prime the automated tests 

./mcr_dev_dev setup_tests

```


# Ways to run api

You can run the server through
nginx
```

#from inside dev_ops
# ./mcr_dev_dev.ah deploy_local_app
```



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

## Update database
This functionality needs to be restored