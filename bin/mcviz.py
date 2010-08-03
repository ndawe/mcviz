#! /usr/bin/env python

from MCViz import EventGraph, parse_options
from MCViz.FeynmanArtist import FeynmanArtist
from MCViz.DualArtist import DualArtist
from sys import argv

def main():
    options, args = parse_options(argv)
    
    if options.debug:
        from IPython.Shell import IPShellEmbed
        ip = IPShellEmbed(["-pdb"], rc_override=dict(quiet=True))

    if len(args) <= 1:
        print "Specify a pythia log file to run on"
        return -1

    event = EventGraph.from_pythia_log(args[1], options)
    
    if options.dual:
        artist = DualArtist(options)
    else:
        artist = FeynmanArtist(options)

    artist.draw(event)

if __name__ == "__main__":
    """
    try:
        import 
    """
    main()
