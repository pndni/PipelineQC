from PipelineQC import main


def test_parse_filter_key_string():
    instr = 'subject=1:2:10'
    assert main._parse_filter_key_string(instr) == ('subject',
                                                    ['1', '2', '10'])
