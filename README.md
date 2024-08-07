Interfaces to queue song paths for Moonbase59's implementation of ices0

# First time setup

cd into project directory and run script `install_setup.sh`

# Set up API for testing

Open terminal in root of project

source mc_dev_ops
```
. ./mc_dev_ops.sh
```

Need to run this so that https will work
```
setup_ssl_cert_local_debug
```

```
# call func to setup unit test environment
# required for vs code test runner
setup_unit_test_env
```

It is also required to run that if we need to update the .env_api template file.
If we update .env_api, we also need to update the setup_env_api_file and
startup_api functions in mc_dev_ops.sh

# Ways to run api

After having sourced mc_dev_ops, run
```
sync_utility_scripts
```
to copy mc_dev_ops to a more central location. Alternatively, you can just cd
to your home directory to run the setup functions.

Next run the start up full web function
```
startup_full_web
```



## end nginx process
If we need to test stuff locally some more but there is an instance running on
nginx, we can try to kill it by calling `kill_process_using_port 8032`

## VSCode debug
Use debug launch profile "Python: API"

# Deploying to server

## Fresh Server
```
./deploy.sh setuplvl=install
```

## Testing new changes
If need to test a new feature, we just run deploy_to_server while that branch
is checked out in git