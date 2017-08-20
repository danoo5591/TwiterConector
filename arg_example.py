# -*- coding: utf-8 -*-

import argparse

class Module(object):
    def __init__(self, name='name'):
        self.name = name

    def a(self, a1, a2):
        print a1, type(a1)
        print a2, type(a2)

    def b(self, b1):
        print b1, type(b1)

if __name__ == '__main__':
    commands = {'a' : Module().a, 'b' : Module().b}
    # create the top-level parser
    parser = argparse.ArgumentParser(prog='PROG')
    # parser.add_argument('method', action='store_true', help='method help')
    subparsers = parser.add_subparsers(dest='command', help='sub-command help')
    # create the parser for the "a" command
    parser_a = subparsers.add_parser('a', help='a help')
    parser_a.add_argument('a1', type=int, help='a1 help')
    parser_a.add_argument('a2', type=int, help='a2 help')
    # create the parser for the "b" command
    parser_b = subparsers.add_parser('b', help='b help')
    parser_b.add_argument('b1', choices='XYZ', help='b1 help')
    # parse some argument lists
    args = vars(parser.parse_args())
    cmd = args.pop('command')
    commands[cmd](**args)
    # module = Module()
    # if args.a:
    #     module.a(args.a1, args.a2)
    # elif args.b:
    #     module.b(args.b1)