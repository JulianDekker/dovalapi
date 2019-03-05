import re


class utils:

    def __init__(self):
        pass

    @staticmethod
    def check_sep(file):
        '''
        searches the first line for the seperator type.
        :param file:
        :return: seperator type
        '''
        with open(file) as f:
            first_line = f.readline()
        if re.search('(.+\t.+)+', first_line):
            return '\t'
        elif re.search('(.+ .+)+', first_line):
            return '\\s'
        elif re.search('(.+,.+)+', first_line):
            return ','
        return None
