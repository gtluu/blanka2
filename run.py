from blanka import *


def run_blanka(args):
    # Args check.
    args_check(args)
    args['version'] = '2.0.0'


if __name__ == '__main__':
    # parse arguments
    args = get_args()

    # Run
    run_blanka(args)
