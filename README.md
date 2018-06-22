# minecraft-rl

- A simple experiment using Malmo with RL-Glue

## Malmo version used

- `Malmo-0.34.0-Windows-64bit_withBoost_Python2.7`
- However, the issue is persistent on `Malmo-0.34.0-Linux-Ubuntu-16.04-64bit_withBoost_Python2.7` as well

## Setup

- Requires Python 2.7 (My Python3 port of RLGlue is is buggy, hence won't suggest using that now)
- Install RLGlue
  - RLGlue server:
    - *Windows:*
        - Extract `prereqs/RLGlueBinary.tar.gz` to some convenient location
        - Add the above location to the `%PATH%`
    - *Linux:*
        - Extract `prereqs/rlglue-3.04.tar.gz` to some convenient location
        - `cd` to the extracted folder
        - Run `configure`
        - Run `make`
        - Run `make install`
    - Test by calling `rl_glue`
    - Output should be something like:
    > ```$ rl_glue
    >     RL-Glue Version 3.04, Build 909
    >     RL-Glue is listening for connections on port=4096
    >  ```
  - Python RLGlue codec:
    - Extract `prereqs/python-codec-dev-2.02.tar.gz` to some convenient location
    - `cd` to the `<extracted folder>/src`
    - Run `python setup.py install`
    - Test by running `python -c "import rlglue"`
    - The above statement should not return any errors

## Usage

- The communication between the agent and environment happens via `rl_glue`
- `run.py` in `mcrl` handles all the necessary steps to start the experiment
- Invoke the experiment as follows:
  - `python -m mcrl.run --load configurations/RandomAgentExperiment.json`

## Notes

- The agent simply returns a random action each step
- (Almost) Everything that happens in the environment and agent are logged in to the `log/<timestamp>.log` file
