#!/usr/bin/env python

import sys
import optparse
import sqlite3
from os.path import exists
from robot.result import ExecutionResult


def main():
    parser = _get_option_parser()
    options = _get_validated_options(parser)
    output_xml_file = ExecutionResult(options.file_path)
    results_dictionary = parse_test_run(output_xml_file)
    print results_dictionary
    # TODO: creating the respective SQL inserts

def parse_test_run(results):
    return {
        'source_file': results.source,
        'generator': results.generator,
        'statistics': parse_statistics(results.statistics),
        'messages': parse_messages(results.errors.messages),
        'suites': parse_suites(results.suite),
    }

def parse_statistics(statistics):
    return {
        'total': get_total_statistics(statistics),
        'tag': get_tag_statistics(statistics),
        'suite': get_suite_statistics(statistics),
    }

def get_total_statistics(statistics):
    return {
        'all': _get_total_stat(statistics.total.all),
        'critical': _get_total_stat(statistics.total.critical),
    }

def _get_total_stat(stat):
    return {
        'name': stat.name,
        'elapsed': stat.elapsed,
        'passed': stat.passed,
        'failed': stat.failed,
        }

def get_tag_statistics(statistics):
    return [_get_parsed_tag_stat(tag) for tag in statistics.tags.tags.values()]

def _get_parsed_tag_stat(stat):
    return {
        'name': stat.name,
        'links': stat.links,
        'doc': stat.doc,
        'non_critical': stat.non_critical,
        'elapsed': stat.elapsed,
        'failed': stat.failed,
        'critical': stat.critical,
        'combined': stat.combined,
        'passed': stat.passed,
        }

def get_suite_statistics(statistics):
    return [_get_parsed_suite_stat(suite.stat) for suite in statistics.suite.suites]

def _get_parsed_suite_stat(stat):
    return {
        'id': stat.id,
        'name': stat.name,
        'elapsed': stat.elapsed,
        'failed': stat.failed,
        'passed': stat.passed,
        }

def parse_suites(suite):
    return [_get_parsed_suite(subsuite) for subsuite in suite.suites]

def _get_parsed_suite(subsuite):
    return {
        'name': subsuite.name,
        'id': subsuite.id,
        'source': subsuite.source,
        'doc': subsuite.doc,
        'start_time': subsuite.starttime,
        'end_time': subsuite.endtime,
        'keywords': parse_keywords(subsuite.keywords),
        'tests': parse_tests(subsuite.tests),
        'suites': parse_suites(subsuite),
        }

def parse_tests(tests):
    return [_get_parsed_test(test) for test in tests]

def _get_parsed_test(test):
    return {
        'id': test.id,
        'name': test.name,
        'timeout': test.timeout,
        'doc': test.doc,
        'status': test.status,
        'tags': parse_tags(test.tags),
        'keywords': parse_keywords(test.keywords),
        }

def parse_keywords(keywords):
    return [_get_parsed_keyword(keyword) for keyword in keywords]

def _get_parsed_keyword(keyword):
    return {
        'name': keyword.name,
        'type': keyword.type,
        'timeout': keyword.timeout,
        'doc': keyword.doc,
        'status': keyword.status,
        'messages': parse_messages(keyword.messages),
        'args': parse_args(keyword.args),
        'keywords': parse_keywords(keyword.keywords)
    }

def parse_args(args):
    return [_get_parsed_arg(arg) for arg in args]

def _get_parsed_arg(arg):
    return {
        'content': arg,
    }

def parse_tags(tags):
    return [_get_parsed_tag(tag) for tag in tags]

def _get_parsed_tag(tag):
    return {
        'content': tag,
    }

def _get_parsed_message(message):
    return {
        'level': message.level,
        'timestamp': message.timestamp,
        'content': message,
    }

def parse_messages(messages):
    return [_get_parsed_message(message) for message in messages]

def _get_option_parser():
    parser = optparse.OptionParser()
    parser.add_option('--file', dest='file_path')
    parser.add_option('--db', dest='db_file_path', default='results.db')
    return parser

def _get_validated_options(parser):
    if len(sys.argv) < 2:
        _exit_with_help(parser)
    options, args = parser.parse_args()
    if args:
        _exit_with_help(parser)
    if not exists(options.file_path):
        _exit_with_help(parser, 'File not found')
    return options

def _exit_with_help(parser, message=None):
    if message:
        sys.stderr.write('Error: %s\n\n' % message)
    parser.print_help()
    exit(1)


class RobotDatabase(object):
    def __init__(self, options):
        self.sql_statements = []
        self.options = options
        self._init_tables()

    def _init_tables(self):
        # TODO: Initialize the tables here
        self.commit()

    def push(self, *sql_statements):
        for statement in sql_statements:
            self.sql_statements.append(statement)

    def commit(self):
        connection = sqlite3.connect(self.options.db_file_path)
        cursor = connection.cursor()
        for statement in self.sql_statements:
            if isinstance(statement, basestring):
                cursor = cursor.execute(statement)
            else:
                cursor = cursor.execute(*statement)
            connection.commit()
        self.sql_statements = []
        connection.close()
        return cursor.lastrowid

if __name__ == '__main__':
    main()