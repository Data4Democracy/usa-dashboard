import re
import os
import datetime
import pandas as pd


class TreasuryStatementParser:
    """Read the raw string data from a treasury statement file.  Get the file date,
    clean irrelevant data out of the file, and break the remainder into individual tables."""

    def __init__(self, file_str):
        self._raw_str = file_str
        self.file_date = self.get_file_date()
        self.tables = self.get_tables()

    def get_file_date(self):
        """Get the date of the file as described in the file header."""
        days = '(?:Sunday|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday)'
        months = '(?:January|February|March|April|May|June|July|August|September|October|November|December)'

        date_ptn = re.compile(f'{days}, ({months} \d\d?, \d\d\d\d)')
        match_text = re.search(date_ptn, self._raw_str).group(1)
        date = datetime.datetime.strptime(match_text, '%B %d, %Y')

        return date

    def _get_relevant_tableset(self):
        """Remove any lines between a line of data and a line of underscores; we assume these are natural
        language descriptions that are not meaningful to the parser."""

        # Establish what a row of data looks like.
        data_row_ptn = re.compile(r' +([a-zA-Z.()\-]+(?: [a-zA-Z.()]+)*)(?:(?: |\$|\d/){2,}((?:\d|,|-|\*)+))+$')
        underscore_row_ptn = re.compile(r' *_{5,}')

        rows = self._raw_str.split('\n')
        most_recent_data_row = None
        most_recent_underscore_row = None
        exclude_intervals = []

        for i, row in enumerate(rows):
            if re.match(data_row_ptn, row):
                most_recent_data_row = i
            if re.match(underscore_row_ptn, row):
                if most_recent_underscore_row is None:
                    # This is the first line of underscores; get rid of everything from the beginning to here.
                    exclude_intervals.append((0, i))
                if most_recent_underscore_row is not None and most_recent_data_row is not None and most_recent_underscore_row < most_recent_data_row:
                    exclude_intervals.append((most_recent_data_row, i))
                most_recent_underscore_row = i

        # Get rid of anything from the last data row to the end of the file.
        if most_recent_data_row is not None:
            exclude_intervals.append((most_recent_data_row, len(rows)))
        filtered_rows = [row for i, row in enumerate(rows) if not any([x[0] < i < x[1] for x in exclude_intervals])]

        return '\n'.join(filtered_rows)

    def get_tables(self):
        """Return a list of substrings, each of which represents a single table."""
        cleansed_file_str = self._get_relevant_tableset()

        data_table_str_ptn = r'(_+\n +TABLE(?:.|\n)*?)'
        table_boundary_str_ptn = r'(?:$| +_+\n(?: +TABLE))'
        data_table_ptn = re.compile(data_table_str_ptn + table_boundary_str_ptn)
        table_boundary_ptn = re.compile(table_boundary_str_ptn)

        matches = []
        working_str = cleansed_file_str
        while True:
            this_match = re.search(data_table_ptn, working_str)
            if this_match is None:
                break

            matches.append(this_match)
            # Remove a line of underscores to break the pattern so we don't find the same match next time.
            working_str = re.sub(table_boundary_ptn, '', working_str, 1)

        return [TreasuryStatementTable(item.group(1)) for item in matches]

    def write_today_data_to_file(self, file_name, sep=','):
        """Write the entire file contents to a delimited file of the following format:
            year, month, day, metric, count
        """
        today_data = []

        for table in self.tables:
            for dataset in table.datasets:
                # If columns are broken out by time period, only collect the ones that describe today; else all.
                if not any('today' in col.lower() for col in dataset.column_names[1:]):
                    relevant_cols = dataset.column_names[1:]
                else:
                    relevant_cols = [col for col in dataset.column_names[1:] if 'today' in col.lower()]

                for col in relevant_cols:
                    data = dataset.get_data()
                    for z in zip(data[dataset.column_names[0]], data[col]):
                        cleansed_col = re.sub(r' ?[Tt]oday', '', col)

                        metric_label = '::'.join([
                            table.table_name,
                            dataset.column_names[0],
                            z[0]
                        ])

                        # Add in the column name, if it's anything other than "Today".
                        metric_label = f"{metric_label}::{cleansed_col}" if cleansed_col else metric_label
                        metric_value = z[1]

                        today_data.append([str(v) for v in [
                                self.file_date.year,
                                self.file_date.month,
                                self.file_date.day,
                                metric_label,
                                metric_value
                            ]
                        ])

        df = pd.DataFrame(today_data, columns=['year', 'month', 'day', 'metric', 'count'])
        df.to_csv(file_name, sep=sep, index=False)


class TreasuryStatementTable:
    """Consume a string representing a single table from the BFS Treasury Statement and parse out the relevant data."""
    def __init__(self, table_str):
        self._raw_str = table_str
        self.table_name = self.get_table_name()
        self.datasets = self.get_datasets()

    def get_datasets(self):
        """Get a list of individual datasets from within the full table string."""
        # Remove the top line of underscores and the line with the table name.
        working_str = self._raw_str
        table_name_ptn = re.compile(r' *_+\n *TABLE(?:.*)?\n')
        working_str = re.sub(table_name_ptn, '', working_str)

        component_ptn = re.compile(r'( *_+(?:.|\n)*?\n *_+(?:.|\n)*?)(?: *_+|$)')
        matches = []

        while True:
            this_match = re.search(component_ptn, working_str)
            if this_match is None:
                break

            matches.append(this_match)
            # Remove the match to break the pattern so we don't find the same match next time.
            working_str = working_str.replace(this_match.group(1), '')

        return [TreasuryStatementDataSet(match.group(1)) for match in matches]

    def get_table_name(self):
        """Pull the table name out of the table name substring component."""
        table_name_ptn = re.compile(r'TABLE\s+[IVXLCM]+(?:-\w)?\s+((?:[a-zA-Z\-]+\s?)+\b)')
        match = re.search(table_name_ptn, self._raw_str)
        if match is None:
            raise Exception('Unable to find table name in supplied string. Table representation appears invalid.')
        else:
            return match.groups()[0]


class TreasuryStatementDataSet:
    """Take a string for a single dataset and extract the data."""
    def __init__(self, dataset_str):
        self._raw_str = dataset_str
        self.column_names = self.get_column_names()

    def get_column_names(self):
        """Parse header section of the dataset string and extract the column names.
        The idea is to find segments of column descriptions on each line, then find other segments
        in similar vertical positions on other lines and merge them into a single description."""

        # Get the top section of the dataset string.
        header_ptn = re.compile(r' *_+(?:.|\n)*?\n *_+')
        header = re.search(header_ptn, self._raw_str).group(0)

        # Define pattern for a "word group": a group of words that appear right next to each other on the same line.
        # We allow at most one space between letters in the same word group;
        # more than one space means we are dealing with separate word groups.
        word_group_ptn = re.compile('(\w+(?:\s\w+)*)')

        # Define a list for the rows of text containing the column labels.
        header_lines = [line for line in header.split('\n') if not re.match('^ ?_+', line)]
        word_groups = []

        # Look for a column name qualifier e.g. "Opening balance"
        # If present, document its location and replace with spaces.
        qualifier = None
        qualifier_span = None
        for i, row in enumerate(header_lines):
            if '___' in row:
                qualifier_span = re.search('_{3,}', row).span()
                qualifier = header_lines[i-1][qualifier_span[0]: qualifier_span[1]].strip()

                space_str = ' ' * (qualifier_span[1] - qualifier_span[0])

                header_lines[i] =\
                    header_lines[i][:qualifier_span[0]]\
                    + space_str\
                    + header_lines[i][qualifier_span[1]:]
                header_lines[i-1] =\
                    header_lines[i-1][:qualifier_span[0]]\
                    + space_str\
                    + header_lines[i-1][qualifier_span[1]:]

        # Find locations of word groups.
        for line in header_lines:
            for match in re.finditer(word_group_ptn, line):
                word_groups.append(match.span())

        # Convert each interval to a set of points and flatten the collection.
        # Flattening has the effect of projecting the multi-line column descriptions vertically,
        # allowing us to slice the header lines into distinct horizontal components for each column.
        occupied_intervals = [range(a, b + 1) for (a, b) in word_groups]
        flat_intervals = [point for str_range in occupied_intervals for point in str_range]

        # Pick out the global max, global min, and any point that has a neighbor not present in the collection.
        # These are the indexes on the edge of a word group.
        interval_endpoints = list(set([
            point for point in flat_intervals
                if point == min(flat_intervals)
                or point == max(flat_intervals)
                or (point - 1) not in flat_intervals
                or (point + 1) not in flat_intervals
        ]))

        # Grab every other interval, as these are the ones that have word groups in them.
        interval_endpoints.sort()
        final_intervals = [
            (interval_endpoints[ind], interval_endpoints[ind + 1])
            for ind, elem in enumerate(interval_endpoints)
            if ind % 2 == 0
        ]

        # Apply the cleanup function to each set of substrings, and add the qualifier if applicable.
        column_list = []
        for interval in final_intervals:
            col = self._get_column_desc_from_indexes(header_lines, interval)
            if qualifier_span is not None and interval[0] >= qualifier_span[0] and interval[1] <= qualifier_span[1]:
                col = qualifier + ' ' + col

            column_list.append(col)

        return column_list

    @staticmethod
    def _get_column_desc_from_indexes(header_str_list, col_tuple):
        return ' '.join([line[col_tuple[0]: col_tuple[1] + 1].strip() for line in header_str_list]).strip()

    def get_data(self):
        """Read the data from the actual rowset and store in a pandas dataframe."""
        rowset_ptn = re.compile('(?:.|\n)*_+\n((?:.|\n)*)$')
        rowset = re.search(rowset_ptn, self._raw_str).group(1)
        rowset_lines = rowset.split('\n')

        # Get rid of the first or last line if it's blank.
        if re.match('^ *$', rowset_lines[0]):
            rowset_lines.pop(0)
        if re.match('^ *$', rowset_lines[-1]):
            rowset_lines.pop(-1)

        # Three cases: data row, qualifier row, or the label doesn't fit on one line.
        multirow_ptn = re.compile(r'^ +([a-zA-Z.()\-:]+(?: [a-zA-Z.()\-:]+)*)(?<!:) *$')
        qualifier_row_ptn = re.compile(r'^ +([a-zA-Z.()\-]+(?: [a-zA-Z.()]+)*): *$')
        data_row_ptn = re.compile(r" +([a-zA-Z.()',\-&/:]+(?: [a-zA-Z.()',\-&/:]+)*)(?:(?: |\$){2,}((?:\d|,|-|\*)+))+")

        # Iterate over the lines, paying special attention to the indents.
        data_list = []

        label_segment = ''
        qualifiers = []

        for i, line in enumerate(rowset_lines):
            # Get the current indentation level. Discard qualifiers that do not contain the current indentation level.
            # The file does not have consistent indentation. If a qualifier is found and indentation is not
            # increased, apply qualifier to the next row only, then discard.
            indent = len(line) - len(line.lstrip(' '))
            qualifiers = [elem for elem in qualifiers if elem.indent < indent or i == elem.line + 1]

            # Check which of the three cases this row falls into.
            multirow_match = re.match(multirow_ptn, line)
            qualifier_row_match = re.match(qualifier_row_ptn, line)
            data_row_match = re.match(data_row_ptn, line)

            if multirow_match:
                label_segment += label_segment and ' ' + multirow_match.group(1) or multirow_match.group(1)
            elif qualifier_row_match:
                qualifier = qualifier_row_match.group(1)
                multirow_prefix = label_segment and label_segment + ' ' or ''
                qualifiers.append(LabelQualifier(indent, multirow_prefix + qualifier, i))
                label_segment = ''
            elif data_row_match:
                delimited_line = re.sub(r'([a-zA-Z0-9()&.])(?: |\$){2,}', r'\1|', line.lstrip())

                # Add in the accumulated qualifiers and descriptor portions and append to data list.
                concatenated_qualifiers = ''.join([qualifier.value + '::' for qualifier in qualifiers])
                multirow_prefix = label_segment and label_segment + ' ' or ''
                this_row_split = (concatenated_qualifiers + multirow_prefix + delimited_line).split('|')
                this_row_cleansed = [elem.replace(',', '') if i > 0 else elem for i, elem in enumerate(this_row_split)]
                data_list.append(this_row_cleansed)

                label_segment = ''
            else:
                raise Exception(f"Row in dataset did not conform to any expected pattern: {line}")

        return pd.DataFrame(data_list, columns=self.column_names)


class LabelQualifier:
    """Small helper class for getting data out of the file."""
    def __init__(self, indent, value, line):
        self.indent = indent
        self.value = value
        self.line = line


if __name__ == '__main__':
    RAW_DIR = os.path.join('data', 'raw')
    PARSED_DIR = os.path.join('data', 'parsed')

    # Check that the working directory contains the expected structure.
    if not all([os.path.isdir(RAW_DIR), os.path.isdir(PARSED_DIR)]):
        raise Exception("Did not find expected directory structure. Exiting.")

    for raw_filename in os.listdir(RAW_DIR):
        raw_file_path = os.path.join(RAW_DIR, raw_filename)

        parsed_filename = 'parsed_' + raw_filename.replace('.txt', '.csv')
        parsed_file_path = os.path.join(PARSED_DIR, parsed_filename)

        if os.path.exists(parsed_file_path):
            print(f"File [{raw_filename}] has already been parsed. Skipping.")
            continue
        else:
            print(f"Parsing file [{raw_filename}]...")

        with open(raw_file_path, 'r') as f:
            raw_content = f.read()

        parser = TreasuryStatementParser(raw_content)
        parser.write_today_data_to_file(parsed_file_path)

        print(f"Finished parsing [{raw_filename}] to [{parsed_filename}].")
