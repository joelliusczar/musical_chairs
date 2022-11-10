Interfaces to queue song paths for Moonbase59's implementation of ices0

# First time setup

cd into project directory and run script `install_setup.sh`

# Set up API for testing

Open terminal in root of project

source radio_common
```
. ./radio_common.sh
```

```
# call func to setup unit test environment
# required for vs code test runner
setup_unit_test_env
```

# Ways to run api

After having sourced radio_common, run
```
sync_utility_scripts
```
to copy radio_common to a more central location. Alternatively, you can just cd
to your home directory to run the setup functions.

Next run the start up full web function
```
startup_full_web
```

If testing and database has been modified, also include `replaceDb`
```
startup_full_web replaceDb
```

## end nginx process
If we need to test stuff locally some more but there is an instance running on
nginx, we can try to kill it by calling `kill_process_using_port 8032`

## VSCode debug
Use debug launch profile Python: API