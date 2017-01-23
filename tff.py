import argparse

from tff.run import main

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Search TCP flows for features.")
    parser.add_argument('-f', type=str, help='Path to feature file directory.', default='features')
    parser.add_argument('-t', type=str, help='Path to tcpflows directory', default='tcpflow_out')
    parser.add_argument('-d', type=str, help="Path to output database", default='tff.db')
    parser.add_argument('-o', type=str, help='Path to output directory', default='tff_out')
    args = parser.parse_args()

    main(args.d, args.f, args.t, args.o)
