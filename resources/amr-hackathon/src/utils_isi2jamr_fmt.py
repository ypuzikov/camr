import codecs
import logging
import re
import argparse
from collections import OrderedDict

from amr import AMR, AMRError
from utils_print import AMRPrinter


class ISI2JAMRAMRPrinter(AMRPrinter):

    def readISI(self, amr_fname):
        """
        Based on: https://github.com/ypuzikov/camr/blob/master/preprocessing.py
        Original: https://github.com/c-amr/camr/blob/master/preprocessing.py

        A method which reads a text file with ISI-aligned AMRs,
        retrieves comments and AMR strings and stores them in two lists.

        :return:
        """
        logging.info('Reading file: %s' % amr_fname)

        amrfile = codecs.open(amr_fname, 'r', encoding='utf-8')
        comment_regex = re.compile("::([^:\s]+)\s(((?!::).)*)")

        comment_list = []
        comment = OrderedDict()
        amr_list = []
        amr_string = ''

        for line in amrfile.readlines():
            if line.startswith('#'):
                for m in comment_regex.finditer(line):
                    comment[m.group(1)] = m.group(2)

                # have to add an # ::snt comment, since CAMR needs it
                comment['snt'] = comment['tok']

            elif not line.strip():
                if amr_string and comment:
                    comment_list.append(comment)
                    amr_list.append(amr_string)
                    amr_string = ''
                    comment = {}

                else:
                    # TODO: check if needed!
                    comment = {}
                    raise NotImplementedError()

            else:
                amr_string += line.strip() + ' '

        if amr_string and comment:
            comment_list.append(comment)
            amr_list.append(amr_string)
        amrfile.close()

        logging.info('Done')

        return (comment_list, amr_list)

    def write_alignment_full(self, comment_list, amr_list, jamr_amr_fname):
        """
        Write AMR string and alignments to a file.
        The alignment info is full -- includes the ::alignment, ::node, ::root and ::edge components
        :param comment_list: list of comment strings
        :param amr_list: list of AMR strings in ISI format
        :param jamr_amr_fname: output file name
        :return:
        """

        logging.info('Writing to file: %s' % jamr_amr_fname)

        with codecs.open(jamr_amr_fname, 'w', encoding='utf-8') as outfile:
            for idx, isi_amr_str in enumerate(amr_list):
                try:
                    amr_obj = AMR(isi_amr_str)
                except AMRError:
                    logging.warning('WARNING: the instance does not comply with AMR specification!')
                    logging.warning('This might be caused by reusing the same var name for several concepts:')
                    logging.warning('%s\n' % isi_amr_str)
                    continue

                # 1. Write comment string
                comment = comment_list[idx]
                comment['snt'] = comment['tok']
                augmented_comment = '\n'.join(['# ::%s %s' % (k, v) for k, v in comment.items()])
                outfile.write('%s\n' % augmented_comment)

                # 2. Write alignments
                ga, relations = self.get_gorn_addr_map(amr_obj)
                full_alignment_info = self.get_amr_alignment_fullinfo(ga, relations)
                outfile.write('%s\n' % full_alignment_info['alignment'])

                # 3. Write node strings
                for v in full_alignment_info['node']:
                    outfile.write('%s\n' % v)

                # 4. Write root string
                outfile.write('%s\n' % full_alignment_info['root'])

                # 5. Write edge strings
                for v in full_alignment_info['edge']:
                    outfile.write('%s\n' % v)

                # 6. Write AMR string
                amr_str_wo_alignments = amr_obj.__str__(alignments=False)
                outfile.write('%s\n\n' % amr_str_wo_alignments)

        logging.info('Done')

    def write_alignment_basic(self, comment_list, amr_list, jamr_amr_fname):
        """
        Write AMR string and alignments to a file.
        The alignment info is basic -- only ::alignment string (w/o ::node, ::root or ::edge components)
        :param comment_list: list of comment strings
        :param amr_list: list of AMR strings in ISI format
        :param jamr_amr_fname: output file name
        :return:
        """

        logging.info('Writing to file: %s' % jamr_amr_fname)

        with codecs.open(jamr_amr_fname, 'w', encoding='utf-8') as outfile:
            for idx, isi_amr_str in enumerate(amr_list):
                try:
                    amr_obj = AMR(isi_amr_str)
                except AMRError:
                    logging.warning('WARNING: the instance does not comply with AMR specification!')
                    logging.warning('This might be caused by reusing the same var name for several concepts:')
                    logging.warning('%s\n' % isi_amr_str)
                    continue

                # 1. Write comment string
                comment = comment_list[idx]
                comment['snt'] = comment['tok']
                augmented_comment = '\n'.join(['# ::%s %s' % (k, v) for k, v in comment.items()])
                outfile.write('%s\n' % augmented_comment)

                # 2. Write alignments
                ga, relations = self.get_gorn_addr_map(amr_obj)
                full_alignment_info = self.get_amr_alignment_fullinfo(ga, relations)
                outfile.write('%s\n' % full_alignment_info['alignment'])

                # 3. Write AMR string
                amr_str_wo_alignments = amr_obj.__str__(alignments=False)
                outfile.write('%s\n\n' % amr_str_wo_alignments)

        logging.info('Done')

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input',
                        help='Input: ISI-aligned AMR file')
    parser.add_argument('-o', '--output',
                        help='Output: ISI-aligned AMR file, but aligned according to the format of JAMR Aligner')

    parser.add_argument('-m', '--mode',
                        help='Mode, specifying the amount of alignment info you want to have in the output.'
                             'Use "full" if you want to have the ::alignment, ::node, ::root and ::edge strings.'
                             'Use "basic", if all you need is the ::alignment string in the output file.',
                        choices=['full', 'basic'], default='basic')


    args = parser.parse_args()
    return args


if __name__ == '__main__':

    logging.basicConfig(level=logging.DEBUG)
    argvs = parse_args()

    input_file = argvs.input
    output_file = argvs.output
    mode = argvs.mode

    printer = ISI2JAMRAMRPrinter()
    comments, amrs = printer.readISI(input_file)

    if mode == 'basic':
        printer.write_alignment_basic(comments, amrs, output_file)
    else:
        printer.write_alignment_full(comments, amrs, output_file)
