#!/usr/bin/env jython

from kahuna.cli.cli import CLI


def main():
    cli = CLI()
    cli.read_options()

if __name__ == "__main__":
    main();

