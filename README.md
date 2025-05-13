Interfaces to queue song paths for Moonbase59's implementation of ices0

# First time setup

cd into `dev_ops` and run script `ruby_dependency_install.sh.sh`

Next run,

`bundle update`

`bundle exec ruby './binstall.rb'`


# Set up API for testing


Need to run this so that https will work
```
mcr_dev setup_debug
```

or if you're in `dev_ops`, run `./mcr_dev_dev setup_debug`

```
To prime the automated tests 

./mcr_dev_dev setup_tests

```


# Ways to run api

After having installed the mcr procs file, you can run the server through
nginx
```
mcr_dev startup_api

mcr_dev setup_client

#or from inside dev_ops
# ./mcr_dev_dev startup_api
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
mcr_dev deploy_install


mcr_dev deploy_api
```

## Testing new changes
If need to test a new feature, we just run`mcr_dev startup_api` while that branch
is checked out in git.
Run `mcr_dev deploy_client` to setup the client.