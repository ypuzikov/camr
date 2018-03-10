from amr import AMR
from utils_print import AMRPrinter


class AMRPrinterTest(AMRPrinter):

    def __init__(self):
        self.amrstring = """(m / multi-sentence~e.10 :snt1~e.10 (i / intense~e.4 :mode interrogative~e.4 :degree (t / too~e.3) :domain (a / article~e.2)) :snt2 (g / good~e.11 :mode interrogative~e.4 :degree (s / so~e.10) :domain (c / country :name (n / name :op1 "united"~e.8 :op2 "states"~e.9))))"""

    # Test functions
    # Not proper tests, just printing routines that allow to observe the results
    def test_get_amr_alignment_string(self, amrstring):
        a = AMR(amrstring)
        ga, relations = self.get_gorn_addr_map(a)
        alignment_str = self.gen_amr_alignment_string(ga)
        return alignment_str

    def test_get_amr_alignment_fullinfo(self, amrstring):
        a = AMR(amrstring)
        ga, relations = self.get_gorn_addr_map(a)
        full_alignment_info = self.get_amr_alignment_fullinfo(ga, relations)

        return full_alignment_info

    def print_test_output(self):

        print('AMR instance:\n%s\n' % AMR(self.amrstring))

        print('Alignment line:\n%s\n' % self.test_get_amr_alignment_string(self.amrstring))

        print('Alignment line + node/root/edge info:')

        alignment_dict = self.test_get_amr_alignment_fullinfo(self.amrstring)
        print(alignment_dict['alignment'])
        for v in alignment_dict['node']:
            print(v)

        print(alignment_dict['root'])
        for v in alignment_dict['edge']:
            print(v)


if __name__ == '__main__':
    AMRPrinterTest().print_test_output()
