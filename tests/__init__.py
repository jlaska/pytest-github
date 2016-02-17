def assert_outcome(result, passed=0, failed=0, skipped=0, xpassed=0, xfailed=0):
    '''This method works around a limitation where pytester assertoutcome()
    doesn't support xpassed and xfailed.
    '''

    actual_count = dict(passed=0, failed=0, skipped=0, xpassed=0, xfailed=0)

    reports = filter(lambda x: hasattr(x, 'when'), result.getreports())
    for report in reports:
        if report.when == 'setup':
            if report.skipped:
                actual_count['skipped'] += 1
        elif report.when == 'call':
            if hasattr(report, 'wasxfail'):
                if report.failed:
                    actual_count['xpassed'] += 1
                elif report.skipped:
                    actual_count['xfailed'] += 1
            else:
                actual_count[report.outcome] += 1
        else:
            continue

    assert passed == actual_count['passed'], "Unexpected value for 'passed', %s" % actual_count
    assert failed == actual_count['failed'], "Unexpected value for 'failed', %s" % actual_count
    assert skipped == actual_count['skipped'], "Unexpected value for 'skipped', %s" % actual_count
    assert xfailed == actual_count['xfailed'], "Unexpected value for 'xfailed', %s" % actual_count
    assert xpassed == actual_count['xpassed'], "Unexpected value for 'xpassed', %s" % actual_count
