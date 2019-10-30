# Michael's Dotfiles for Linux OS

(This repo is a work in progress on the first machine, so the installation steps here might be wrong / insufficient)

These dotfiles use the Python package [Homely](https://github.com/phodge/homely/).

## Installation

1. Install homely
2. Clone this dotfiles repo
3. Run homely update

## Usage

`homely update` in terminal to run `HOMELY.py`, which is the central script which sets everything up.
Edit the files in the "scripts" folder to customize shell setup and package installations.

### Symlinks & Config files

- Make sure you have the desired config file in your dotfiles repo.
- Create the necessary symlink line in HOMELY.py
- Delete the unwanted config file from your machine
- Run `homely update` in terminal.