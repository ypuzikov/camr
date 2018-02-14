import codecs
import logging
import re
import sys
from collections import OrderedDict

from amr import AMR, AMRError
from utils_print import AMRPrinter

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class ISI2JAMRAMRPrinter(AMRPrinter):

    def readISI(self, amr_fname):
        """
        Based on: https://github.com/ypuzikov/camr/blob/master/preprocessing.py
        Original: https://github.com/c-amr/camr/blob/master/preprocessing.py

        A method which reads a text file with ISI-aligned AMRs,
        retrieves comments and AMR strings and stores them in two lists.

        :return:
        """
        logger.info('Reading file: %s' % amr_fname)

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

                # TODO: check if needed!
                else:
                    comment = {}
            else:
                amr_string += line.strip() + ' '

        if amr_string and comment:
            comment_list.append(comment)
            amr_list.append(amr_string)
        amrfile.close()

        logger.info('Done')

        return (comment_list, amr_list)

    def write_JAMR(self, comment_list, amr_list, jamr_amr_fname):

        logger.info('Writing to file: %s' % jamr_amr_fname)

        with codecs.open(jamr_amr_fname, 'w', encoding='utf-8') as outfile:
            for idx, isi_amr_str in enumerate(amr_list):
                try:
                    amr_obj = AMR(isi_amr_str)
                except AMRError:
                    warning_msg = 'WARNING: the instance does not comply with AMR specification!'
                    expl_msg = 'This might be caused by reusing the same var name for several concepts:'
                    print(warning_msg)
                    print(expl_msg)
                    print('%s\n' % isi_amr_str)
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

        logger.info('Done')


if __name__ == '__main__':

    argvs = sys.argv
    input_file = sys.argv[1]

    if len(argvs) == 2:
        output_file = '%s.jamr_fmt' % input_file
    elif len(argvs) == 3:
        output_file = sys.argv[2]
    else:
        raise RuntimeError('Specify input and output (optional) files!')

    printer = ISI2JAMRAMRPrinter()
    comments, amrs = printer.readISI(input_file)
    printer.write_JAMR(comments, amrs, output_file)
